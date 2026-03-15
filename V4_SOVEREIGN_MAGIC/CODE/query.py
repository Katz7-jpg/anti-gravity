import os
import sys
import json
from typing import List, Dict, Any

from dotenv import load_dotenv
from supabase import create_client, Client

# --- CONFIGURATION (V5 APEX) ---
load_dotenv(r"d:\AI_FACTORY\.env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("CRITICAL: Missing credentials in .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- QUERY_PHASE ENGINE (APEX NEURAL MAP) ---
class SovereignQueryEngine:
    def __init__(self):
        # We prioritize Neural Map (Graph) and Contextual Soul over raw vectors
        pass

    def search(self, query_text: str, top_k: int = 5):
        print(f"QUERY: {query_text} | PHASE 1: Neural Map & Soul Search...")
        
        # 1. Vector + FTS Hybrid Search (Discovery)
        try:
            res = supabase.table("v4_vault").select("id, filename, content, context_soul, metadata").ilike("content", f"%{query_text}%").limit(top_k).execute()
            hits = res.data or []
        except Exception as e:
            print(f"Notice: Vault access error: {e}")
            hits = []

        if not hits:
            print("Zero matches found in Vault.")
            return []

        # 2. PHASE 2: Graph Expansion (The 100,000x Hack)
        # For each hit, we pull its relations from v4_graph
        expanded_hits = []
        doc_ids = [hit['id'] for hit in hits]
        
        try:
            graph_res = supabase.table("v4_graph").select("*").in_("doc_id", doc_ids).execute()
            relations = graph_res.data or []
        except Exception as e:
            print(f"Relational Mapping Offline: {e}")
            relations = []

        # 3. Context Augmentation
        for hit in hits:
            doc_id = hit['id']
            # Find relations for this doc
            doc_rels = [f"{r['subject']} -> {r['relation']} -> {r['object']}" for r in relations if r['doc_id'] == doc_id]
            
            # Inject Neural Map into the view
            hit['neural_map'] = doc_rels
            expanded_hits.append(hit)

        return expanded_hits

def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py \"Your Question\"")
        return
        
    query = sys.argv[1]
    engine = SovereignQueryEngine()
    
    hits = engine.search(query)
    
    print("\n" + "="*60)
    print("--- V5 APEX PROTOCOL: NEURAL MAP RESULTS ---")
    print("="*60)
    
    for i, hit in enumerate(hits):
        print(f"\n[{i+1}] SOURCE: {hit['filename']}")
        print(f"--- DOCUMENT SOUL ---")
        print(f"{hit.get('context_soul', 'N/A')}")
        
        if hit.get('neural_map'):
            print(f"--- NEURAL CONNECTIONS ---")
            for rel in hit['neural_map'][:5]:
                print(f"  • {rel}")
        
        print(f"--- CORE LOGIC ---")
        content = hit['content']
        # Clean XML if present
        if "<content>" in content:
            content = content.split("<content>")[1].split("</content>")[0]
        print(f"{content[:300]}...")
        print("-" * 40)

if __name__ == "__main__":
    main()
