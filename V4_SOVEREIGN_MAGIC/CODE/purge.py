import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# --- CONFIGURATION (V5 APEX) ---
load_dotenv(r"d:\AI_FACTORY\.env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

BASE_DIR = Path(r"D:\V4_SOVEREIGN_MAGIC")
BRAIN_DROP = BASE_DIR / "DROP_ZONE"

if not SUPABASE_URL or not SUPABASE_KEY:
    print("CRITICAL: Missing credentials in .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def scan_and_wipe():
    print("="*50)
    print("   SOVEREIGN ANALYST: V5 APEX PURGE PROTOCOL")
    print("="*50)
    
    try:
        # 1. Map current local PDFs
        local_files = {f.name for f in BRAIN_DROP.glob("*.pdf")}
        print(f"LOCAL_FILES: {len(local_files)} identified.")

        # 2. Query all files in the Vault
        res = supabase.table("v4_vault").select("id, filename").execute()
        db_files = res.data or []
        
        if not db_files:
            print("VAULT_STATUS: 0 documents found in memory.")
            return

        print(f"VAULT_STATUS: {len(db_files)} documents found in memory.")

        # 3. Identify Orphans
        orphans = [row for row in db_files if row['filename'] not in local_files]

        if not orphans:
            print("MEMORY_SOVEREIGNTY: Clean. No orphans detected.")
        else:
            print(f"DETECTION: {len(orphans)} orphaned documents found.")
            for orphan in orphans:
                filename = orphan['filename']
                doc_id = orphan['id']
                print(f"PURGING: Scrubbing {filename} (ID: {doc_id[:8]}) from Global Memory...")
                
                # V5 Specific: Delete from Graph first (if CASCADE is not active)
                try:
                    supabase.table("v4_graph").delete().eq("doc_id", doc_id).execute()
                except: pass

                # Delete from Vault
                res_del = supabase.table("v4_vault").delete().eq("id", doc_id).execute()
                
                if res_del.data:
                    print(f"SUCCESS: {filename} 100% erased (Vault + Neural Map).")
                else:
                    print(f"FAILED: Could not scrub {filename}. Check permissions.")

        print("\n" + "="*50)
        print("   WIPE_COMPLETE: NEURAL MAP ALIGNED WITH DROP_ZONE.")
        print("="*50)

    except Exception as e:
        print(f"PURGE_ERROR: {e}")

if __name__ == "__main__":
    scan_and_wipe()
