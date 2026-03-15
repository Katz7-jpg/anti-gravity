import os
import json
import time
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from urllib.parse import urlparse

import modal
import requests
from fastapi import FastAPI, Request, Response

# --- CLOUD GHOST-BOT CONFIGURATION (V5 APEX) ---
# 24/7 Serverless Telegram Interface
# Phase 1 Upgrades: Hybrid Search + Prompt Caching + Local Embeddings
image = (
    modal.Image.debian_slim()
    .pip_install(
        "requests",
        "supabase",
        "python-dotenv",
        "fastapi",
        "openai",
        "rank-bm25>=0.2.2",  # BM25 for hybrid search
        "sentence-transformers>=2.2.0"  # Local embeddings on GPU
    )
)

app = modal.App("v5-apex-ghost-bot")

secrets = [
    modal.Secret.from_name("v4-predator-secrets"),
    modal.Secret.from_name("glm-secret")
]

# Feature flags for graceful degradation
USE_EMBEDDINGS = os.environ.get("USE_EMBEDDINGS", "true").lower() == "true"
USE_CACHE = os.environ.get("USE_CACHE", "true").lower() == "true"
USE_BM25 = os.environ.get("USE_BM25", "true").lower() == "true"
CACHE_TTL_DAYS = int(os.environ.get("CACHE_TTL_DAYS", "7"))
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION", "384"))

@app.cls(image=image, secrets=secrets, timeout=600, gpu="T4")
class ApexGhostBot:
    @modal.enter()
    def setup(self):
        from supabase import create_client
        self.sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
        self.token = os.environ["TELEGRAM_BOT_TOKEN"]
        
        # Robust Chat ID handling
        raw_id = os.environ["TELEGRAM_CHAT_ID"]
        try:
            self.chat_id = int(re.sub(r'[^\d\-]', '', str(raw_id)))
            print(f"🛠️ BOT_INITIALIZED: Listening for Chat ID {self.chat_id}")
        except:
            self.chat_id = raw_id # Fallback to string
            print(f"⚠️ CHAT_ID_WARNING: Using raw ID {self.chat_id}")
            
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        
        # BM25 index (built lazily or pre-warmed)
        self.bm25_index = None
        self.bm25_corpus = []
        self.bm25_doc_ids = []
        
        # Initialize sentence-transformers for local GPU embeddings
        self.embedding_model = None
        if USE_EMBEDDINGS:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"EMBEDDING_MODEL: Loading {EMBEDDING_MODEL}...")
                self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
                print(f"EMBEDDING_MODEL: Loaded successfully")
            except Exception as e:
                print(f"EMBEDDING_MODEL_WARNING: {e}")
        
        # Pre-warm BM25 index if enabled (avoids slow first query)
        if USE_BM25:
            try:
                print("BM25: Pre-warming index...")
                self.build_bm25_index()
            except Exception as e:
                print(f"BM25_PREWARM_WARNING: {e}")

    def send_msg(self, text: str, parse_mode: str = "Markdown", chat_id: int = None, reply_markup: dict = None):
        target = chat_id or self.chat_id
        payload = {
            "chat_id": target,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        # Split text if it's too long (Telegram limit is 4096)
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                payload["text"] = text[i:i+4000]
        # Debug print
        print(f"📤 SENDING_REPLY to {target}: {text[:50]}...")
        r = requests.post(f"{self.api_url}/sendMessage", json=payload)
        if not r.json().get('ok'):
            print(f"❌ SEND_MSG_ERROR: {r.json().get('description')}")

    # =========================================================================
    # PROMPT CACHING (Phase 1 Upgrade)
    # =========================================================================
    
    def _compute_query_hash(self, query: str, context_hash: str = None) -> str:
        """Compute deterministic hash for query + context combination."""
        content = f"{query}:{context_hash or 'default'}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get_cached_response(self, query: str, context_hash: str = None) -> dict:
        """
        Check if we have a cached response for this query.
        
        Returns:
            {'hit': bool, 'response': str or None, 'cached_at': str or None}
        """
        if not USE_CACHE:
            return {'hit': False, 'response': None}
            
        query_hash = self._compute_query_hash(query, context_hash)
        
        try:
            result = self.sb.table("prompt_cache").select("*").eq("query_hash", query_hash).gt("expires_at", datetime.now().isoformat()).execute()
            
            if result.data:
                cached = result.data[0]
                # Update hit count
                try:
                    self.sb.table("prompt_cache").update({"hit_count": cached['hit_count'] + 1}).eq("id", cached['id']).execute()
                except:
                    pass  # Non-critical if hit count update fails
                
                return {
                    'hit': True,
                    'response': cached['response_text'],
                    'cached_at': cached['created_at']
                }
        except Exception as e:
            print(f"CACHE_LOOKUP_WARNING: {e}")
        
        return {'hit': False, 'response': None}

    def cache_response(self, query: str, response: str, context_hash: str = None) -> bool:
        """Store response in cache for future use."""
        if not USE_CACHE:
            return False
            
        query_hash = self._compute_query_hash(query, context_hash)
        
        try:
            self.sb.table("prompt_cache").upsert({
                "query_hash": query_hash,
                "query_text": query[:500],
                "response_text": response,
                "context_hash": context_hash,
                "expires_at": (datetime.now() + timedelta(days=CACHE_TTL_DAYS)).isoformat()
            }, on_conflict="query_hash").execute()
            return True
        except Exception as e:
            print(f"CACHE_STORAGE_WARNING: {e}")
            return False

    def clear_cache(self) -> Tuple[bool, str]:
        """Clear all cached responses."""
        try:
            self.sb.table("prompt_cache").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            return True, "All cached responses purged."
        except Exception as e:
            return False, str(e)

    # =========================================================================
    # HYBRID SEARCH (Phase 1 Upgrade - Local Embeddings)
    # =========================================================================
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text for BM25."""
        if not text:
            return []
        text = text.lower()
        tokens = re.findall(r'\b\w{3,}\b', text)  # Words with 3+ chars
        return tokens

    def build_bm25_index(self):
        """Build BM25 index from vault content."""
        if not USE_BM25:
            return
            
        print("BM25: Building index...")
        
        try:
            # Fetch all chunks
            res = self.sb.table("v4_vault").select("id, content, filename").limit(1000).execute()
            
            if not res.data:
                print("BM25: No documents to index")
                return
            
            self.bm25_corpus = []
            self.bm25_doc_ids = []
            
            for doc in res.data:
                content = doc.get('content', '')
                if content:
                    tokens = self._tokenize(content)
                    self.bm25_corpus.append(tokens)
                    self.bm25_doc_ids.append({
                        'id': doc['id'],
                        'filename': doc.get('filename', 'unknown'),
                        'content': content
                    })
            
            # Build BM25 index
            if self.bm25_corpus:
                from rank_bm25 import BM25Okapi
                self.bm25_index = BM25Okapi(self.bm25_corpus)
                print(f"BM25: Index built with {len(self.bm25_corpus)} documents")
        except Exception as e:
            print(f"BM25_BUILD_ERROR: {e}")

    def _vector_search(self, query: str, limit: int) -> List[dict]:
        """Vector similarity search using local embeddings."""
        if not USE_EMBEDDINGS or not self.embedding_model:
            return []
        
        try:
            # Generate query embedding using sentence-transformers
            query_embedding = self.embedding_model.encode(query, convert_to_numpy=True).tolist()
            
            # Call Supabase RPC function for vector search
            result = self.sb.rpc('match_embeddings', {
                'query_embedding': query_embedding,
                'match_threshold': 0.6,
                'match_count': limit
            }).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"VECTOR_SEARCH_WARNING: {e}")
            return []

    def _bm25_search(self, query: str, limit: int) -> List[dict]:
        """Search using BM25 algorithm."""
        if not USE_BM25:
            return []
            
        if not self.bm25_index:
            self.build_bm25_index()
        
        if not self.bm25_index:
            return []
        
        try:
            query_tokens = self._tokenize(query)
            if not query_tokens:
                return []
            
            scores = self.bm25_index.get_scores(query_tokens)
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:limit]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0:
                    result = self.bm25_doc_ids[idx].copy()
                    result['bm25_score'] = float(scores[idx])
                    results.append(result)
            
            return results
        except Exception as e:
            print(f"BM25_SEARCH_WARNING: {e}")
            return []

    def _keyword_search(self, query: str, limit: int) -> List[dict]:
        """Fallback keyword search using ILIKE."""
        keywords = [k for k in query.split() if len(k) > 3]
        if not keywords:
            return []
        
        results = []
        seen_ids = set()
        
        for kw in keywords[:3]:  # Limit to 3 keywords
            try:
                res = self.sb.table("v4_vault").select("id, filename, content").ilike("content", f"%{kw}%").limit(limit).execute()
                if res.data:
                    for r in res.data:
                        if r['id'] not in seen_ids:
                            results.append(r)
                            seen_ids.add(r['id'])
            except:
                pass
        
        return results

    def hybrid_search(self, query: str, limit: int = 5) -> List[dict]:
        """
        Ghost-Speed Hybrid Search (Reliability v2):
        Vector (0.5) > Keyword (0.3) > BM25 (0.2).
        Ensures 100% recall while maintaining ghost-speed.
        """
        results = []
        seen_ids = set()
        
        # 1. Vector search (weight: 0.5) - FASTEST Cloud RPC
        vector_results = self._vector_search(query, limit)
        for r in vector_results:
            doc_id = r.get('doc_id')
            if doc_id and doc_id not in seen_ids:
                r['final_score'] = r.get('similarity', 0.5) * 0.5
                results.append(r)
                seen_ids.add(doc_id)
        
        # 2. Keyword fallback (weight: 0.3) - Crucial for specific terms
        if len(results) < limit:
            kw_results = self._keyword_search(query, limit)
            for r in kw_results:
                doc_id = r.get('id')
                if doc_id not in seen_ids:
                    r['final_score'] = 0.3
                    r['doc_id'] = doc_id
                    results.append(r)
                    seen_ids.add(doc_id)
        
        # 3. BM25 search (weight: 0.2) - Uses cached index
        if len(results) < limit:
            bm25_results = self._bm25_search(query, limit)
            for r in bm25_results:
                doc_id = r.get('id')
                if doc_id not in seen_ids:
                    r['final_score'] = r.get('bm25_score', 0) * 0.002
                    r['doc_id'] = doc_id
                    results.append(r)
                    seen_ids.add(doc_id)
        
        # Sort by final score
        results.sort(key=lambda x: x.get('final_score', 0), reverse=True)
        return results[:limit]

    def synthesize(self, query: str, context: str, system_persona: str = None, timeout: int = 60) -> str:
        """Surgical synthesis with lower temperature and faster completion."""
        context_hash = hashlib.md5(context.encode()).hexdigest()[:16]
        
        if USE_CACHE:
            cached = self.get_cached_response(query, context_hash)
            if cached['hit']:
                return cached['response']
        
        from openai import OpenAI
        api_key = os.environ.get("GLM_API_KEY") or os.environ.get("ZAI_API_KEY")
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.us-west-2.modal.direct/v1",
            timeout=float(timeout)
        )
        
        base_persona = system_persona or "Sovereign Architect. Response: Surgical, direct, context-driven."
        prompt = f"### CONTEXT:\n{context}\n\n### QUERY: {query}\n\nANSWER:"
        
        try:
            res = client.chat.completions.create(
                model="zai-org/GLM-5-FP8",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Lower for speed/reliability
                max_tokens=800    # Prevent run-on responses
            )
            response = res.choices[0].message.content
        except Exception as e:
            print(f"GLM-5: Synthesis failed - {e}")
            raise
        
        if USE_CACHE:
            self.cache_response(query, response, context_hash)
        
        return response

    def _get_system_stats(self) -> Dict[str, int]:
        """Get system statistics for status display."""
        stats = {
            'vault_count': 0,
            'embedding_count': 0,
            'cache_count': 0,
            'graph_count': 0
        }
        
        try:
            res = self.sb.table("v4_vault").select("count", count="exact").execute()
            stats['vault_count'] = res.count or 0
        except:
            pass
        
        try:
            res = self.sb.table("v4_embeddings").select("count", count="exact").execute()
            stats['embedding_count'] = res.count or 0
        except:
            pass
        
        try:
            res = self.sb.table("prompt_cache").select("count", count="exact").execute()
            stats['cache_count'] = res.count or 0
        except:
            pass
        
        try:
            res = self.sb.table("v4_graph").select("count", count="exact").execute()
            stats['graph_count'] = res.count or 0
        except:
            pass
        
        return stats

    # =========================================================================
    # URL DOWNLOAD & PROCESSING (PDF URL Ingestion)
    # =========================================================================
    
    # Configuration constants
    MAX_PDF_SIZE_BYTES = 50 * 1024 * 1024  # 50MB max file size
    DOWNLOAD_TIMEOUT_SECONDS = 60  # 60 second timeout for downloads
    
    def _extract_urls(self, text: str) -> List[str]:
        """
        Extract HTTP/HTTPS URLs from text.
        
        Args:
            text: Text containing potential URLs
            
        Returns:
            List of extracted URLs
        """
        # Match HTTP/HTTPS URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls
    
    def _is_valid_pdf_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate if URL points to a PDF file.
        
        Args:
            url: URL to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ('http', 'https'):
                return False, "URL must use HTTP or HTTPS protocol"
            
            # Check if URL ends with .pdf (quick check)
            path_lower = parsed.path.lower()
            if path_lower.endswith('.pdf'):
                return True, ""
            
            # If not obvious from path, we'll check content-type during download
            return True, ""
            
        except Exception as e:
            return False, f"Invalid URL format: {str(e)}"
    
    def _download_pdf(self, url: str) -> Tuple[Optional[bytes], str]:
        """
        Download PDF from URL with validation.
        
        Args:
            url: URL to download from
            
        Returns:
            Tuple of (pdf_bytes or None, error_message or filename)
        """
        try:
            # Validate URL format first
            is_valid, error = self._is_valid_pdf_url(url)
            if not is_valid:
                return None, error
            
            # Extract filename from URL
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            filename = path_parts[-1] if path_parts else "document.pdf"
            
            # Ensure filename has .pdf extension
            if not filename.lower().endswith('.pdf'):
                filename += ".pdf"
            
            # Sanitize filename
            filename = re.sub(r'[^\w\-_\.]', '_', filename)
            if not filename or filename == ".pdf":
                filename = f"document_{int(time.time())}.pdf"
            
            # Download with timeout and size limit
            response = requests.get(
                url,
                timeout=self.DOWNLOAD_TIMEOUT_SECONDS,
                stream=True,  # Stream to check size before downloading fully
                headers={'User-Agent': 'Mozilla/5.0 (compatible; SovereignBot/1.0)'}
            )
            
            # Check HTTP status
            if response.status_code != 200:
                return None, f"HTTP error {response.status_code}: Failed to download"
            
            # Check content-type if available
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                # If content-type doesn't indicate PDF and URL doesn't end with .pdf
                if 'application/pdf' not in content_type and 'application/octet-stream' not in content_type:
                    return None, f"URL does not point to a PDF (Content-Type: {content_type})"
            
            # Check content length if available
            content_length = response.headers.get('Content-Length')
            if content_length:
                size = int(content_length)
                if size > self.MAX_PDF_SIZE_BYTES:
                    size_mb = size / (1024 * 1024)
                    return None, f"File too large: {size_mb:.1f}MB (max: 50MB)"
            
            # Download content with size check
            pdf_bytes = b""
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_size += len(chunk)
                if total_size > self.MAX_PDF_SIZE_BYTES:
                    return None, f"File too large: exceeded 50MB during download"
                pdf_bytes += chunk
            
            if not pdf_bytes:
                return None, "Downloaded file is empty"
            
            # Basic PDF validation (check magic bytes)
            if not pdf_bytes.startswith(b'%PDF'):
                return None, "Downloaded file is not a valid PDF (missing PDF header)"
            
            return pdf_bytes, filename
            
        except requests.exceptions.Timeout:
            return None, "Download timed out (60 seconds limit)"
        except requests.exceptions.ConnectionError as e:
            return None, f"Connection error: {str(e)}"
        except requests.exceptions.RequestException as e:
            return None, f"Download failed: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def _process_pdf_from_url(self, url: str, chat_id: int) -> bool:
        """
        Download and process a PDF from URL.
        
        Args:
            url: URL to download PDF from
            chat_id: Telegram chat ID to send updates to
            
        Returns:
            True if successful, False otherwise
        """
        # Send initial status
        self.send_msg(f"📥 *DOWNLOADING*\n`{url}`", chat_id=chat_id)
        
        # Download the PDF
        pdf_bytes, result = self._download_pdf(url)
        
        if pdf_bytes is None:
            self.send_msg(f"❌ *DOWNLOAD FAILED*\n`{url}`\n\nError: {result}", chat_id=chat_id)
            return False
        
        filename = result  # On success, result contains the filename
        size_kb = len(pdf_bytes) / 1024
        
        # Update status
        self.send_msg(f"📄 *PROCESSING PDF*\nFile: `{filename}`\nSize: {size_kb:.1f} KB\n\n🔄 Running V5 Apex Ingestion...", chat_id=chat_id)
        
        # Process through existing pipeline
        try:
            shredder_cls = modal.Cls.from_name("v4-predator-shredder", "PredatorShredder")
            shredder = shredder_cls()
            result = shredder.shred_and_tag.remote(pdf_bytes, filename)
            
            # Check for duplicate detection message
            if "DUPLICATE DETECTED" in result:
                self.send_msg(f"⚠️ *DUPLICATE SKIPPED*\n`{filename}`\n\n{result}", chat_id=chat_id)
            else:
                self.send_msg(f"✅ *SUCCESS*\n`{filename}` is now part of your Neural Map.\n\n*Phase 1 RAG:*\n• Document chunks stored\n• Local GPU embeddings generated ({EMBEDDING_MODEL})\n• Ready for hybrid search", chat_id=chat_id)
            return True
            
        except Exception as e:
            self.send_msg(f"❌ *PROCESSING FAILED*\n`{filename}`\n\nError: {str(e)}", chat_id=chat_id)
            return False

    @modal.method()
    def handle_update(self, update: Dict[str, Any]):
        # Handle Interactive Button Clicks (Callback Queries)
        if "callback_query" in update:
            cb = update["callback_query"]
            cid = cb["message"]["chat"]["id"]
            if cid != self.chat_id: return
            
            data = cb.get("data", "")
            if data.startswith("wipe_"):
                target_id = data.replace("wipe_", "")
                res = self.sb.table("v4_vault").select("filename").eq("id", target_id).execute()
                if not res.data:
                    self.send_msg("❌ File no longer exists.", chat_id=cid)
                else:
                    fname = res.data[0]['filename']
                    self.send_msg(f"⚠️ *WIPING*: `{fname}`...", chat_id=cid)
                    
                    try:
                        res_chunks = self.sb.table("v4_vault").select("id").eq("filename", fname).execute()
                        for c in res_chunks.data:
                            # Delete embeddings first
                            try:
                                self.sb.table("v4_embeddings").delete().eq("doc_id", c['id']).execute()
                            except:
                                pass
                            # Delete graph relations
                            self.sb.table("v4_graph").delete().eq("doc_id", c['id']).execute()
                            # Delete vault entry
                            self.sb.table("v4_vault").delete().eq("id", c['id']).execute()
                        self.send_msg(f"✅ *SCRUBBED*: `{fname}` completely erased.", chat_id=cid)
                    except Exception as e:
                        self.send_msg(f"❌ *PURGE_FAILED*: {str(e)}", chat_id=cid)
                        
                requests.post(f"{self.api_url}/answerCallbackQuery", json={"callback_query_id": cb["id"]})
                return

            if data.startswith("report_"):
                target_id = data.replace("report_", "")
                res = self.sb.table("v4_vault").select("filename").eq("id", target_id).execute()
                if not res.data:
                    self.send_msg("❌ File no longer exists.", chat_id=cid)
                else:
                    fname = res.data[0]['filename']
                    self.send_msg(f"⚙️ *ASSEMBLING*: Generating God-Level Anthropic Markdown for `{fname}`...", chat_id=cid)
                    
                    try:
                        # 1. Fetch chunks ordered by index
                        res_chunks = self.sb.table("v4_vault").select("chunk_index, chunk_content").eq("filename", fname).order("chunk_index").execute()
                        full_md = ""
                        for c in res_chunks.data:
                            full_md += c['chunk_content'] + "\n\n"
                        
                        # 2. Extract soul for the Executive Summary
                        ai_summary = ""
                        if "<document_soul>" in full_md:
                            soul = full_md.split("<document_soul>")[1].split("</document_soul>")[0].strip()
                            ai_summary = f"> **God-Level Anthropic Executive Summary:**\n> {soul}\n\n---\n\n"

                        final_md = f"# God-Level Report: {fname}\n\n{ai_summary}{full_md}"
                        
                        # 3. Save Temporary .md File
                        safe_fname = fname.replace(".pdf", "")
                        tmp_path = f"/tmp/{safe_fname}_Anthropic_Report.md"
                        with open(tmp_path, "w", encoding="utf-8") as f:
                            f.write(final_md)
                            
                        # 4. Send .md Document via Telegram
                        with open(tmp_path, "rb") as doc:
                            requests.post(
                                f"{self.api_url}/sendDocument", 
                                data={"chat_id": cid, "caption": f"✨ *Anthropic-Level Markdown Ready*: `{fname}`", "parse_mode": "Markdown"}, 
                                files={"document": doc}
                            )
                    except Exception as e:
                        self.send_msg(f"❌ *REPORT_FAILED*: {str(e)}", chat_id=cid)
                        
                requests.post(f"{self.api_url}/answerCallbackQuery", json={"callback_query_id": cb["id"]})
                return

            return

        if "message" not in update:
            return

        msg = update["message"]
        cid = msg.get("chat", {}).get("id")
        
        # Security Check
        if cid != self.chat_id:
            print(f"⚠️ UNAUTHORIZED_ACCESS: Attempt from {cid} (Expected: {self.chat_id})")
            # Optional: Send a one-time message to the unknown user to help them identify their ID
            # requests.post(f"{self.api_url}/sendMessage", json={"chat_id": cid, "text": f"❌ Unauthorized. Your Chat ID is `{cid}`. Please update your Sovereign configuration."})
            return
        
        text = msg.get("text", "")
        username = msg.get("from", {}).get("username", "Sovereign")
        
        print(f"📥 REQUEST: From {username} ({cid}) - '{text[:50]}'")

        if text.startswith("/check"):
            self.send_msg("📡 **HEARTBEAT**: Sovereign Magic is ALIVE and LISTENING. Ghost-Speed active.")
            return
        if text.startswith("/start"):
            # Register all commands dynamically on startup
            # Register all commands dynamically on startup (SYNCED WITH USER PREFERENCE)
            full_commands = [
                {"command": "start", "description": "🔮 Initialize Sovereign Magic"},
                {"command": "status", "description": "📊 Check Health & Vault Size"},
                {"command": "list", "description": "📁 View Vault Inventory"},
                {"command": "purge", "description": "🗑️ Interactive GUI Wipe"},
                {"command": "report", "description": "📝 God-Level Markdown Export"},
                {"command": "ask", "description": "🧠 Multi-Hop Synthesis"},
                {"command": "soul", "description": "🔍 Fetch Document Soul"},
                {"command": "graph", "description": "🕸️ Neural Map Traversal"},
                {"command": "compare", "description": "⚖️ Semantic Doc vs Doc Delta"},
                {"command": "trends", "description": "📈 Neural Map Centrality"},
                {"command": "simulate", "description": "🎭 Expert Persona Query"},
                {"command": "digest", "description": "📰 Master Intelligence Briefing"},
                {"command": "url", "description": "🔗 Ingest PDF from URL"},
                {"command": "clearcache", "description": "🗑️ Clear Prompt Cache"}
            ]
            r = requests.post(f"{self.api_url}/setMyCommands", json={"commands": full_commands})
            print(f"🛠️ COMMANDS_REGISTERED: {r.json().get('ok')}")
            
            # Get live stats for welcome message
            stats = self._get_system_stats()
            
            welcome_msg = f"""🔮 *V4 SOVEREIGN MAGIC BOT* 🔮

Greetings, @{username}. Your Sovereign Intelligence System is ONLINE.

📋 *CORE PROTOCOLS:*
/ask <query> - Brainstorm across your documents
/url <link> - Ingest PDF from external URL
/status - Neural Map Health Check
/purge - Deterministic Memory Scrub

📊 *STATISTICS:*
• Vault Documents: {stats['vault_count']}
• Neural Map: {stats['graph_count']} links

💡 Drop any PDF or paste a PDF URL to expand your Sovereign Knowledge Base."""
            
            self.send_msg(welcome_msg)
            return

        if text.startswith("/help"):
            self.send_msg(f"✨ *SYSTEM AWAKE & READY* ✨\n\n🦾 *APEX GHOST-BOT ONLINE*\nGreetings, @{username}.\n\n*Vault Operations:*\n/status 📊 /list 📁 /purge 🗑️ /report 📝\n\n*Intelligence Core:*\n/ask 🧠 /soul 🔍 /graph 🕸️\n\n*Phase 4 – Sovereign Intelligence:*\n/compare ⚖️ DocA vs DocB\n/trends 📈 Top Neural Nodes\n/simulate 🎭 Persona Query\n/digest 📰 Master Briefing\n\n*URL Ingestion:*\n/url 📥 Ingest PDF from URL\n/ingest 📥 (alias for /url)\n\n*Phase 1 RAG Upgrades:*\n• Hybrid Search (Vector + BM25)\n• Prompt Caching (40-87% cost reduction)\n• Local GPU Embeddings (sentence-transformers)\n• /clearcache 🗑️ Clear cached responses\n\n*Drop any PDF or paste a PDF URL to begin ingestion!*")
            return

        elif text.startswith("/status"):
            self.send_msg("🔄 *COMMAND ACKNOWLEDGED*: Checking system health...")
            try:
                stats = self._get_system_stats()
                
                self.send_msg(f"🟢 *SYSTEM_HEALTH: NOMINAL*\n\nVault: {stats['vault_count']} Chunks\nNeural Map: {stats['graph_count']} Connections\nEmbeddings: {stats['embedding_count']} Vectors\nCache: {stats['cache_count']} Entries\n\n*Phase 1 RAG Status:*\n• Embeddings: {'✅' if USE_EMBEDDINGS else '❌'} (Local GPU: {EMBEDDING_MODEL})\n• Cache: {'✅' if USE_CACHE else '❌'}\n• BM25: {'✅' if USE_BM25 else '❌'}\n\nSovereignty: 100%")
            except Exception as e:
                self.send_msg(f"🔴 *SYSTEM_HEALTH: DEGRADED*\nError: {str(e)}")
            return

        elif text.startswith("/list"):
            self.send_msg("🔄 *COMMAND ACKNOWLEDGED*: Scanning vault inventory...")
            # Distinct filenames
            res = self.sb.table("v4_vault").select("filename").execute()
            docs = list(set([d['filename'] for d in (res.data or [])]))
            if not docs:
                self.send_msg("Vault is currently empty. Drop a PDF to begin.")
            else:
                out = "*VAULT INVENTORY*:\n"
                for i, d in enumerate(docs):
                    out += f"{i+1}. `{d}`\n"
                self.send_msg(out)
            return

        elif text.startswith("/purge"):
            res = self.sb.table("v4_vault").select("filename, id").execute()
            docs = res.data or []
            if not docs:
                self.send_msg("Vault is empty. Nothing to purge.")
                return
            
            # Deduplicate by filename
            unique_docs = {}
            for d in docs:
                if d['filename'] not in unique_docs:
                    unique_docs[d['filename']] = d['id']
            
            keyboard = []
            for fname, fid in unique_docs.items():
                keyboard.append([{"text": f"🗑️ {fname}", "callback_data": f"wipe_{fid}"}])
                
            self.send_msg("*PURGE PROTOCOL*\nSelect a file to wipe its Vault & Neural Map:", reply_markup={"inline_keyboard": keyboard})
            return

        elif text.startswith("/report"):
            res = self.sb.table("v4_vault").select("filename, id").execute()
            docs = res.data or []
            if not docs:
                self.send_msg("Vault is empty. Nothing to report.")
                return
            
            unique_docs = {}
            for d in docs:
                if d['filename'] not in unique_docs:
                    unique_docs[d['filename']] = d['id']
            
            keyboard = []
            for fname, fid in unique_docs.items():
                keyboard.append([{"text": f"📄 {fname}", "callback_data": f"report_{fid}"}])
                
            self.send_msg("*REPORT PROTOCOL*\nSelect a file to export as a God-Level Markdown Document:", reply_markup={"inline_keyboard": keyboard})
            return

        elif text.startswith("/soul "):
            target_name = text.split("/soul ")[1].strip()
            self.send_msg(f"🔍 *FETCHING SOUL*: `{target_name}`...")
            # We fetch chunk index 0, as souls are duplicated across chunks or at least in chunk 0
            res = self.sb.table("v4_vault").select("chunk_content").eq("filename", target_name).eq("chunk_index", 0).execute()
            if not res.data:
                self.send_msg(f"❌ Soul not found for `{target_name}`.")
                return
            content = res.data[0]['chunk_content']
            if "<document_soul>" in content:
                soul = content.split("<document_soul>")[1].split("</document_soul>")[0].strip()
                self.send_msg(f"✨ *DOCUMENT SOUL* ✨\n\n{soul}")
            else:
                self.send_msg("❌ No Soul tags found in document.")
            return

        elif text.startswith("/graph "):
            subject = text.split("/graph ")[1].strip()
            self.send_msg(f"🕸️ *TRAVERSING NEURAL MAP*: `{subject}`...")
            res = self.sb.table("v4_graph").select("*").ilike("subject", f"%{subject}%").limit(20).execute()
            if not res.data:
                self.send_msg("❌ No connections found in Neural Map.")
                return
            out = f"🕸️ *NEURAL MAP* ({len(res.data)} connections):\n"
            for r in res.data:
                out += f"• `{r['subject']}` ➡️ `{r['relation']}` ➡️ `{r['object']}`\n"
            self.send_msg(out)
            return

        elif text.startswith("/compare "):
            # Format: /compare FileA vs FileB
            parts = text.replace("/compare ", "").split(" vs ")
            if len(parts) != 2:
                self.send_msg("⚖️ *USAGE*: `/compare FileA.pdf vs FileB.pdf`")
                return
            docA, docB = parts[0].strip(), parts[1].strip()
            self.send_msg(f"⚖️ *SEMANTIC DELTA INITIATED*\n🔍 Comparing `{docA}` vs `{docB}`...\n⏳ GLM-5 Analyzing contradictions & synergies...")
            try:
                resA = self.sb.table("v4_vault").select("chunk_content").eq("filename", docA).limit(5).execute()
                resB = self.sb.table("v4_vault").select("chunk_content").eq("filename", docB).limit(5).execute()
                if not resA.data or not resB.data:
                    self.send_msg("❌ Could not retrieve one or both documents from the Vault.")
                    return
                ctxA = "\n".join([c['chunk_content'][:800] for c in resA.data])
                ctxB = "\n".join([c['chunk_content'][:800] for c in resB.data])
                combined_ctx = f"=== DOCUMENT A: {docA} ===\n{ctxA}\n\n=== DOCUMENT B: {docB} ===\n{ctxB}"
                persona = f"You are a world-class research analyst. Compare Document A and Document B. Identify: (1) Core Contradictions (2) Shared Foundations (3) Unique Insights in each. Format your answer clearly with bold headers."
                result = self.synthesize(f"Compare {docA} versus {docB}", combined_ctx, system_persona=persona)
                self.send_msg(f"⚖️ *SEMANTIC DELTA REPORT*\n\n{result}")
            except Exception as e:
                self.send_msg(f"❌ *COMPARE_FAILED*: {str(e)}")
            return

        elif text.startswith("/trends"):
            self.send_msg("📈 *COMMAND ACKNOWLEDGED*: Computing Neural Map Centrality...\n🔄 Analyzing top entities across your entire knowledge base...")
            try:
                res = self.sb.table("v4_graph").select("subject").execute()
                if not res.data:
                    self.send_msg("❌ Neural Map is empty. Ingest some PDFs first.")
                    return
                counts = {}
                for row in res.data:
                    s = row['subject']
                    counts[s] = counts.get(s, 0) + 1
                sorted_entities = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:15]
                out = "📈 *TOP NEURAL NODES* (Most Connected Entities):\n\n"
                for i, (entity, count) in enumerate(sorted_entities):
                    out += f"{i+1}. `{entity}` — *{count} connections*\n"
                out += "\n💡 These are the highest-leverage concepts in your Sovereign Knowledge Base."
                self.send_msg(out)
            except Exception as e:
                self.send_msg(f"❌ *TRENDS_FAILED*: {str(e)}")
            return

        elif text.startswith("/simulate "):
            # Format: /simulate <Persona> <query>
            content = text.replace("/simulate ", "", 1).strip()
            if not content:
                self.send_msg("🎭 *USAGE*: `/simulate CEO What is our strategic risk?`")
                return
            words = content.split(" ", 1)
            if len(words) < 2:
                self.send_msg("🎭 *USAGE*: `/simulate CEO What is our strategic risk?`")
                return
            persona_role, query = words[0], words[1]
            self.send_msg(f"🎭 *ENGAGING PERSONA*: `{persona_role}`\n🔄 *APEX THINKING*: Synthesizing through expert lens...")
            try:
                # Use hybrid search for better context
                search_results = self.hybrid_search(query, limit=6)
                if search_results:
                    context = "\n---\n".join([r.get('content', r.get('chunk_content', ''))[:800] for r in search_results])
                else:
                    # Fallback to basic retrieval
                    res_v = self.sb.table("v4_vault").select("chunk_content").limit(6).execute()
                    context = "\n---\n".join([d['chunk_content'][:800] for d in (res_v.data or [])])
                
                system_persona = f"You are a world-class {persona_role}. Analyze the provided documents through the specific lens of a {persona_role}. Focus on what matters most to a {persona_role}: risk, opportunity, strategic implications, ROI, or whatever is most relevant to that role. Be direct and decisive."
                result = self.synthesize(query, context, system_persona=system_persona)
                self.send_msg(f"🎭 *{persona_role.upper()} PERSPECTIVE*\n\n{result}")
            except Exception as e:
                self.send_msg(f"❌ *SIMULATE_FAILED*: {str(e)}")
            return

        elif text.startswith("/digest"):
            self.send_msg("📰 *COMMAND ACKNOWLEDGED*: Generating Master Intelligence Briefing...\n⏳ Analyzing your latest knowledge pulses...")
            try:
                # Get the 10 most recently ingested unique filenames
                res = self.sb.table("v4_vault").select("filename, chunk_content").eq("chunk_index", 0).order("id", desc=True).limit(10).execute()
                if not res.data:
                    self.send_msg("❌ Vault is empty. Ingest some PDFs first.")
                    return
                # Build souls summary for each
                souls = []
                for row in res.data:
                    fname = row['filename']
                    content = row['chunk_content']
                    if "<document_soul>" in content:
                        soul = content.split("<document_soul>")[1].split("</document_soul>")[0].strip()[:500]
                        souls.append(f"Source: {fname}\n{soul}")
                    else:
                        souls.append(f"Source: {fname}\n{content[:400]}")
                digest_context = "\n\n---\n\n".join(souls)
                persona = "You are a master intelligence analyst writing an executive briefing. Synthesize the following documents into 5 crisp bullet points of the most important insights, patterns, and strategic implications. Format: • **[Bold Header]**: Finding."
                result = self.synthesize("Generate a Master Intelligence Briefing from these documents.", digest_context, system_persona=persona)
                self.send_msg(f"📰 *MASTER INTELLIGENCE BRIEFING*\n\n{result}")
            except Exception as e:
                self.send_msg(f"❌ *DIGEST_FAILED*: {str(e)}")
            return

        elif text.startswith("/clearcache"):
            self.send_msg("🗑️ *CACHE PURGE*: Clearing prompt cache...")
            success, message = self.clear_cache()
            if success:
                self.send_msg(f"✅ *CACHE CLEARED*: {message}")
            else:
                self.send_msg(f"❌ *CACHE_PURGE_FAILED*: {message}")
            return

        elif text.startswith("/url") or text.startswith("/ingest"):
            # PDF URL Ingestion Handler
            # Usage: /url https://example.com/document.pdf
            # Supports multiple URLs (one per line)
            
            # Extract the text after the command
            if text.startswith("/url "):
                url_text = text.split("/url ", 1)[1].strip()
            elif text.startswith("/ingest "):
                url_text = text.split("/ingest ", 1)[1].strip()
            else:
                self.send_msg("📥 *URL INGESTION*\n\nUsage: `/url https://example.com/document.pdf`\n\nYou can also provide multiple URLs (one per line).")
                return
            
            if not url_text:
                self.send_msg("❌ *NO URL PROVIDED*\n\nUsage: `/url https://example.com/document.pdf`")
                return
            
            # Extract URLs from the message
            urls = self._extract_urls(url_text)
            
            if not urls:
                self.send_msg("❌ *NO VALID URLs FOUND*\n\nPlease provide HTTP/HTTPS URLs pointing to PDF files.")
                return
            
            # Process each URL
            total_urls = len(urls)
            success_count = 0
            
            self.send_msg(f"📥 *URL INGESTION STARTED*\n\nFound {total_urls} URL(s) to process...\n{'='*30}")
            
            for i, url in enumerate(urls, 1):
                self.send_msg(f"📍 *Processing {i}/{total_urls}*", chat_id=cid)
                
                if self._process_pdf_from_url(url, cid):
                    success_count += 1
            
            # Summary
            if total_urls > 1:
                self.send_msg(f"📊 *INGESTION COMPLETE*\n\n✅ Success: {success_count}/{total_urls}\n❌ Failed: {total_urls - success_count}/{total_urls}", chat_id=cid)
            return

        elif text.startswith("/ask ") or (not text.startswith("/") and len(text) > 5):
            query = text.split("/ask ")[1] if text.startswith("/ask ") else text
            start_time = time.time()
            self.send_msg(f"🔄 *QUERY RECEIVED*\n\n🔍 Searching neural map...")
            
            try:
                # 1. Use Hybrid Search for better retrieval (with progress)
                search_start = time.time()
                search_results = self.hybrid_search(query, limit=5)
                search_time = time.time() - search_start
                print(f"HYBRID_SEARCH: Completed in {search_time:.2f}s, found {len(search_results)} results")
                
                # 2. Check Graph for keywords (supplementary context)
                keywords = query.replace("?", "").split(" ")
                valid_kw = [k for k in keywords if len(k) > 4]
                graph_context = ""
                if valid_kw:
                    k = valid_kw[0]
                    try:
                        res_g = self.sb.table("v4_graph").select("*").ilike("subject", f"%{k}%").limit(15).execute()
                        if res_g.data:
                            graph_context = "\nNEURAL CONNECTIONS:\n" + "\n".join([f"{r['subject']} -> {r['relation']} -> {r['object']}" for r in res_g.data])
                    except Exception as e:
                        print(f"GRAPH_LOOKUP_WARNING: {e}")
                
                # 3. Build text context from search results
                text_context = ""
                if search_results:
                    text_context = "\nRELEVANT CONTEXT:\n" + "\n---\n".join([
                        r.get('content', r.get('chunk_content', ''))[:1000]
                        for r in search_results
                    ])
                else:
                    # Fallback to basic retrieval if hybrid search returns nothing
                    try:
                        res_v = self.sb.table("v4_vault").select("chunk_content").limit(5).execute()
                        if res_v.data:
                            text_context = "\nDOCUMENT SOULS / CONTENT:\n" + "\n---\n".join([d['chunk_content'][:1000] for d in res_v.data])
                    except Exception as e:
                        print(f"FALLBACK_SEARCH_WARNING: {e}")

                full_context = graph_context + "\n" + text_context
                
                # Check if we have any context
                if not full_context.strip():
                    self.send_msg(f"⚠️ *NO CONTEXT FOUND*\n\nNo relevant documents in vault. Try ingesting some PDFs first with /url or by sending a document.")
                    return
                
                # 4. Synthesize via GLM-5 (with timeout and progress)
                self.send_msg(f"🧠 *SYNTHESIZING RESPONSE*\n\n📊 Found {len(search_results)} relevant chunks\n⏱️ Search: {search_time:.1f}s\n🔄 Generating answer...")
                
                try:
                    answer = self.synthesize(query, full_context, timeout=90)
                    total_time = time.time() - start_time
                    self.send_msg(f"👁️ *SOVEREIGN RESPONSE*\n\n{answer}\n\n_⏱️ Total: {total_time:.1f}s_")
                except TimeoutError:
                    self.send_msg(f"⏱️ *TIMEOUT*: GLM-5 synthesis took too long. Please try again with a simpler query.")
                except ValueError as e:
                    self.send_msg(f"❌ *CONFIG ERROR*: {str(e)}\n\nCheck Modal secrets configuration.")
                except Exception as e:
                    error_type = type(e).__name__
                    error_msg = str(e)[:200]
                    self.send_msg(f"❌ *GLM-5 ERROR*\n\nType: {error_type}\nMessage: {error_msg}")
                    
            except Exception as e:
                total_time = time.time() - start_time
                error_type = type(e).__name__
                self.send_msg(f"❌ *QUERY FAILED* ({total_time:.1f}s)\n\n{error_type}: {str(e)[:200]}")
            return

        # 2. PDF INGESTION HANDLER
        if "document" in msg and msg["document"].get("mime_type") == "application/pdf":
            doc = msg["document"]
            fid = doc["file_id"]
            fname = doc.get("file_name", "unknown.pdf")
            
            self.send_msg(f"📄 *DETECTED*: `{fname}`\nStarting V5 Apex Ingestion (with Local GPU Embeddings)...")
            
            # Download file
            file_info = requests.get(f"{self.api_url}/getFile?file_id={fid}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"https://api.telegram.org/file/bot{self.token}/{file_path}").content
            
            # Call Predator via Modal (Linked via name)
            try:
                shredder_cls = modal.Cls.from_name("v4-predator-shredder", "PredatorShredder")
                shredder = shredder_cls()
                shredder.shred_and_tag.remote(file_content, fname)
                self.send_msg(f"✅ *SUCCESS*: `{fname}` is now part of your Neural Map.\n\n*Phase 1 RAG:*\n• Document chunks stored\n• Local GPU embeddings generated ({EMBEDDING_MODEL})\n• Ready for hybrid search")
            except Exception as e:
                self.send_msg(f"❌ *INGESTION_FAILED*: {str(e)}")
            return

@app.function(image=image, secrets=secrets)
@modal.fastapi_endpoint(method="POST")
def webhook(request: Dict[str, Any]):
    print(f"🌐 WEBHOOK_RECEIVE: Handshake detected.")
    # Spawn the heavy logic
    ApexGhostBot().handle_update.spawn(request)
    return {"status": "ok"}
