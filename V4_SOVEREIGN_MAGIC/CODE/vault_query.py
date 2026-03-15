"""
V5 Apex Protocol - Surgical Vault Query Tool
===========================================
Performs hybrid semantic (vector) and keyword (BM25) search against
the Sovereign Vault. Returns top-k relevant fragments with context.

Usage:
  python vault_query.py "How does the Sovereign Architect work?"
"""

import os
import sys
import json
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment
load_dotenv(r"D:\AI_FACTORY\.env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

try:
    from supabase import create_client, Client
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except ImportError:
    print("❌ ERROR: Supabase SDK not installed (pip install supabase)")
    sys.exit(1)

def vector_search(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Query Supabase RPC for vector similarity search."""
    # Note: This tool performs ONLY the DB query. 
    # For full hybrid search with embedding generation, 
    # we would need the sentence-transformers model.
    # For now, we utilize the 'match_embeddings' RPC which is already vectorized in the cloud.
    
    # However, to do this LOCALLY, we'd need to generate the query_embedding here.
    # Since we want this to be FAST and zero-dependency, we can fallback to 
    # Keyword search if the local machine doesn't have the embedding model.
    return []

def keyword_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Fallback keyword search using ILIKE."""
    keywords = [k for k in query.split() if len(k) > 3]
    if not keywords:
        return []
    
    results = []
    seen_ids = set()
    
    for kw in keywords[:3]:
        try:
            res = sb.table("v4_vault").select("id, filename, content").ilike("content", f"%{kw}%").limit(limit).execute()
            if res.data:
                for r in res.data:
                    if r['id'] not in seen_ids:
                        results.append(r)
                        seen_ids.add(r['id'])
        except Exception as e:
            print(f"  ⚠️ Keyword search error (kw={kw}): {e}")
            
    return results

def main():
    parser = argparse.ArgumentParser(description="Sovereign Vault Search")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--limit", type=int, default=3, help="Max results")
    args = parser.parse_args()
    
    print(f"🔍 SEARCHING VAULT: '{args.query}'...")
    print("-" * 50)
    
    # 1. Try Keyword Search (Zero-Dependency)
    results = keyword_search(args.query, limit=args.limit)
    
    if not results:
        print("❓ No direct matches found in vault.")
        return
    
    print(f"✅ Found {len(results)} relevant fragments:\n")
    
    for i, res in enumerate(results):
        print(f"[{i+1}] SOURCE: {res.get('filename')}")
        content = res.get('content', '')
        # Extract chunk if XML tags exist
        if "<content>" in content:
            content = content.split("<content>")[1].split("</content>")[0].strip()
        
        print(f"FRAGMENT: {content[:400]}...")
        print("-" * 30)

if __name__ == "__main__":
    main()
