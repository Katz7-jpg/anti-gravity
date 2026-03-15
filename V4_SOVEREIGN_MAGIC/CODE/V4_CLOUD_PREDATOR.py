import os
import hashlib
import time
import json
from typing import List, Optional

import modal

# --- CLOUD PREDATOR CONFIGURATION (V5 APEX PROTOCOL) ---
# Optimized for GraphRAG + Agentic Extraction + Embedding Generation
# Updated: Using sentence-transformers for local GPU embeddings (no API costs)
image = (
    modal.Image.debian_slim()
    .pip_install(
        "marker-pdf==1.10.2",
        "supabase",
        "openai",
        "python-dotenv",
        "tiktoken>=0.5.0",  # Token counting for chunking
        "sentence-transformers>=2.2.0"  # Local embeddings on GPU
    )
)

app = modal.App("v4-predator-shredder")

# Secrets required:
# - GLM_API_KEY (for GLM-5 inference)
# - SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
secrets = [
    modal.Secret.from_name("glm-secret"),
    modal.Secret.from_name("v4-predator-secrets")
]

# Feature flags for graceful degradation
USE_EMBEDDINGS = os.environ.get("USE_EMBEDDINGS", "true").lower() == "true"
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION", "384"))  # all-MiniLM-L6-v2 dimension

@app.cls(image=image, secrets=secrets, cpu=4, memory=16384, gpu="T4", timeout=1200)
class PredatorShredder:
    @modal.enter()
    def setup(self):
        from supabase import create_client
        self.sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
        
        # Lazy load Marker (High-Fidelity OCR)
        from marker.models import create_model_dict
        from marker.converters.pdf import PdfConverter
        self.converter = PdfConverter(artifact_dict=create_model_dict())
        
        # Initialize sentence-transformers for local GPU embeddings
        self.embedding_model = None
        if USE_EMBEDDINGS:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
                print(f"EMBEDDING_MODEL: Loaded {EMBEDDING_MODEL} (dimension: {EMBEDDING_DIMENSION})")
            except Exception as e:
                print(f"EMBEDDING_MODEL_WARNING: Failed to load sentence-transformers: {e}")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text chunk using sentence-transformers.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        if not self.embedding_model or not USE_EMBEDDINGS:
            return None
            
        if not text or len(text.strip()) == 0:
            return None
            
        try:
            # Truncate to 8K chars max (sentence-transformers handles this well)
            truncated_text = text[:8000] if len(text) > 8000 else text
            
            # Generate embedding using sentence-transformers (runs on GPU)
            embedding = self.embedding_model.encode(truncated_text, convert_to_numpy=True)
            
            return embedding.tolist()
            
        except Exception as e:
            print(f"EMBEDDING_ERROR: Failed to generate embedding: {e}")
            return None

    def generate_embeddings(self, text_chunks: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple text chunks efficiently.
        
        Args:
            text_chunks: List of text chunks to embed
            
        Returns:
            List of embeddings (each is a list of floats or None if failed)
        """
        if not self.embedding_model or not USE_EMBEDDINGS:
            return [None] * len(text_chunks)
        
        try:
            # Filter valid chunks
            valid_chunks = [(i, chunk) for i, chunk in enumerate(text_chunks) if chunk and len(chunk.strip()) > 0]
            
            if not valid_chunks:
                return [None] * len(text_chunks)
            
            # Batch encode for efficiency (sentence-transformers is optimized for batches)
            indices, chunks = zip(*valid_chunks)
            truncated_chunks = [c[:8000] if len(c) > 8000 else c for c in chunks]
            
            embeddings_array = self.embedding_model.encode(list(truncated_chunks), convert_to_numpy=True)
            
            # Build result list
            results = [None] * len(text_chunks)
            for idx, embedding in zip(indices, embeddings_array):
                results[idx] = embedding.tolist()
            
            return results
            
        except Exception as e:
            print(f"EMBEDDING_BATCH_ERROR: {e}")
            return [None] * len(text_chunks)

    def chunk_text(self, text: str, max_chunk_size: int = 2000, document_soul: str = "") -> List[str]:
        """
        Split text into chunks for embedding with Anthropic Contextual Retrieval.
        
        Uses document_soul as context prefix for each chunk, improving retrieval
        accuracy by 30-50% per Anthropic's research.
        
        Args:
            text: The text to chunk
            max_chunk_size: Maximum characters per chunk
            document_soul: Document summary to prepend as context (Anthropic Contextual Retrieval)
            
        Returns:
            List of text chunks with document context prepended
        """
        if not text:
            return []
            
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            # If adding this paragraph would exceed max size
            if len(current_chunk) + len(para) + 2 > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # ANTHROPIC CONTEXTUAL RETRIEVAL: Prepend document_soul to each chunk
        # This improves retrieval accuracy by 30-50% by giving each chunk
        # the document's overall context
        if document_soul and chunks:
            contextualized_chunks = []
            for chunk in chunks:
                contextualized = f"[DOCUMENT CONTEXT: {document_soul}]\n\n[CHUNK CONTENT]:\n{chunk}"
                contextualized_chunks.append(contextualized)
            return contextualized_chunks
        
        return chunks

    @modal.method()
    def shred_and_tag(self, file_bytes: bytes, filename: str) -> str:
        print(f"--- APEX_ANALYSIS_START: {filename} ---")
        
        # 0. HASH GUARD DEDUPLICATION (SHA-256 Local-First Skip Logic)
        # Pre-check if document already exists to avoid wasting GPU cycles and storage
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()
        print(f"HASH_GUARD: SHA-256 = {sha256_hash[:16]}...")
        
        try:
            existing = self.sb.table("v4_vault").select("id, filename, created_at").eq("doc_hash", sha256_hash).execute()
            if existing.data:
                existing_doc = existing.data[0]
                print(f"HASH_GUARD_SKIP: Document already exists!")
                print(f"  - Existing ID: {existing_doc['id']}")
                print(f"  - Original filename: {existing_doc['filename']}")
                print(f"  - Uploaded at: {existing_doc['created_at']}")
                return f"⚠️ DUPLICATE DETECTED: Document '{filename}' already exists in vault as '{existing_doc['filename']}' (uploaded {existing_doc['created_at']}). Skipping processing to save GPU cycles."
        except Exception as e:
            print(f"HASH_GUARD_WARNING: Could not check for duplicates: {e}. Proceeding with processing.")
        
        # 1. THE SHRED (Marker PDF-to-Markdown)
        temp_path = f"/tmp/{filename}"
        with open(temp_path, "wb") as f:
            f.write(file_bytes)
        
        rendered = self.converter(temp_path)
        md_content = rendered.markdown
        file_hash = sha256_hash  # Use SHA-256 instead of MD5 for doc_hash

        # 2. GLM-5 AGENTIC EXTRACTION (Neural Map Protocol)
        from openai import OpenAI
        
        # Use Modal API endpoint (same as V5_GHOST_BOT)
        api_key = os.environ.get("MODAL_API_KEY") or os.environ.get("GLM_API_KEY")
        base_url = os.environ.get("GLM_BASE_URL", "https://api.us-west-2.modal.direct/v1")
        model_name = os.environ.get("GLM_MODEL", "zai-org/GLM-5-FP8")
        
        if not api_key:
            print("APEX_EXTRACTION_FAILURE: No API key configured (MODAL_API_KEY or GLM_API_KEY)")
            doc_soul = "Apex Protocol Offline. API key not configured."
            entities = []
        else:
            client = OpenAI(api_key=api_key, base_url=base_url, timeout=60.0)
            
            apex_prompt = f"""
Analyze this document with 'Agentic Thinking' for a V5 GraphRAG system (Apex Protocol).
1. Create a 100-word <document_soul> summarizing executive intent and logical hierarchy.
2. Extract a JSON list of key entities and their relationships.
   FORMAT: [{{"sub": "NAME", "rel": "VERB/RELATION", "obj": "TARGET", "type": "PERSON|ORG|PROJECT|CONCEPT"}}]
   FOCUS: High-value connections only.
<doc>{md_content[:15000]}</doc>
""".strip()
            
            print(f"INJECTING APEX SOUL & NEURAL MAP (GLM-5 via {base_url})...")
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": apex_prompt}],
                    temperature=0.3
                )
                raw_response = response.choices[0].message.content
                
                # Extract Soul and Graph with more flexibility
                doc_soul = response.choices[0].message.content[:500] # Default
                entities = []
                
                # Use broader markers
                if "<document_soul>" in raw_response:
                    doc_soul = raw_response.split("<document_soul>")[1].split("</document_soul>")[0].strip()
                elif "SUMMARY:" in raw_response:
                    doc_soul = raw_response.split("SUMMARY:")[1].split("\n\n")[0].strip()
                
                # If no markers, use the first 500 chars as the soul if JSON follows
                if "```json" in raw_response:
                    json_part = raw_response.split("```json")[1].split("```")[0].strip()
                    entities = json.loads(json_part)
                    if doc_soul.strip() == "": # If soul extraction failed above
                       doc_soul = raw_response.split("```json")[0].strip()[:500]
                elif "[" in raw_response and "]" in raw_response:
                    # Use regex or simple search for the first array
                    start = raw_response.find("[")
                    end = raw_response.rfind("]") + 1
                    try:
                        entities = json.loads(raw_response[start:end])
                        if doc_soul.strip() == "":
                            doc_soul = raw_response[:start].strip()[:500]
                    except: pass
                
                print(f"APEX_EXTRACTION_SUCCESS: Soul extracted ({len(doc_soul)} chars), {len(entities)} entities")

            except Exception as e:
                print(f"APEX_EXTRACTION_FAILURE: {type(e).__name__}: {e}")
                doc_soul = f"Apex Protocol Offline. Error: {str(e)[:100]}"
                entities = []

        # 3. XML STRUCTURAL TAGGING (V5 Spec)
        xml_payload = f"""
<document_soul>{doc_soul}</document_soul>
<neural_map_summary>{json.dumps(entities[:10])}</neural_map_summary>
<chunk_metadata>Source: {filename} | ID: {file_hash}</chunk_metadata>
<content>{md_content}</content>
""".strip()

        # 4. VAULT SYNC (Supabase Ghost-Sync V5)
        print(f"GHOST_SYNC: Pushing {filename} to v4_vault...")
        try:
            res = self.sb.table("v4_vault").insert({
                "doc_hash": file_hash,
                "filename": filename,
                "content": xml_payload,
                "context_soul": doc_soul,
                "metadata": {"filename": filename, "source": "v5-apex-predator", "entities": len(entities)}
            }).execute()
            print(f"GHOST_SYNC_SUCCESS: {filename} anchored in vault.")
            doc_uuid = res.data[0]['id'] if res.data else None
        except Exception as e:
            print(f"GHOST_SYNC_ERROR: Failed to anchor {filename} in vault: {str(e)}")
            doc_uuid = None

        # 5. NEURAL MAP INTEGRATION (Graph Store)
        if doc_uuid and entities:
            print(f"NEURAL_MAP: Syncing {len(entities)} relations to v4_graph...")
            graph_data = [
                {
                    "doc_id": doc_uuid,
                    "subject": e.get("sub", "Unknown"),
                    "relation": e.get("rel", "Related_To"),
                    "object": e.get("obj", "Unknown"),
                    "metadata": {"type": e.get("type", "CONCEPT")}
                }
                for e in entities if "sub" in e and "obj" in e
            ]
            try:
                self.sb.table("v4_graph").insert(graph_data).execute()
                print("NEURAL_MAP_SUCCESS: Relations linked.")
            except Exception as e:
                print(f"NEURAL_MAP_BYPASS: Table 'v4_graph' not active. Skipping graph store. Error: {e}")

        # 6. EMBEDDING GENERATION (Phase 1 RAG Upgrade - Local GPU + Contextual Retrieval)
        if doc_uuid and USE_EMBEDDINGS:
            print(f"EMBEDDING: Generating vectors for {filename} using {EMBEDDING_MODEL}...")
            print(f"CONTEXTUAL_RETRIEVAL: Using document_soul as context prefix for chunks...")
            try:
                # Chunk the markdown content WITH document_soul context (Anthropic Contextual Retrieval)
                chunks = self.chunk_text(md_content, document_soul=doc_soul)
                
                if chunks:
                    # Generate embeddings for all chunks (batch mode)
                    embeddings = self.generate_embeddings(chunks)
                    
                    # Store embeddings with chunk references and content
                    stored_count = 0
                    for i, (chunk_content, embedding) in enumerate(zip(chunks, embeddings)):
                        if embedding:
                            try:
                                self.sb.table("v4_embeddings").insert({
                                    "doc_id": doc_uuid,
                                    "chunk_index": i,
                                    "embedding": embedding,
                                    "content": chunk_content,  # Store contextualized chunk for retrieval
                                    "content_hash": hashlib.md5(chunk_content.encode()).hexdigest()
                                }).execute()
                                stored_count += 1
                            except Exception as e:
                                print(f"EMBEDDING_STORE_ERROR: Chunk {i}: {e}")
                    
                    print(f"EMBEDDING_SUCCESS: {stored_count}/{len(chunks)} contextualized vectors stored")
                    
                    # Update vault record with content hash
                    try:
                        self.sb.table("v4_vault").update({
                            "content_hash": hashlib.md5(md_content.encode()).hexdigest()
                        }).eq("id", doc_uuid).execute()
                    except Exception as e:
                        print(f"VAULT_HASH_UPDATE_WARNING: {e}")
                        
            except Exception as e:
                print(f"EMBEDDING_FAILURE: {e}")
                print("EMBEDDING_FALLBACK: Document stored without embeddings. Keyword search will still work.")

        print(f"--- APEX_ANALYSIS_COMPLETE: {filename} ---")
        return md_content
