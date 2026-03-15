import os
import sys
import hashlib
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Set, Union

from dotenv import load_dotenv
from supabase import create_client, Client
import modal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION (V5 APEX MAGIC) ---
load_dotenv(r"d:\AI_FACTORY\.env")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
MODAL_API_KEY = os.environ.get("MODAL_API_KEY")

# Auth Bridge Support
MODAL_TOKEN_ID = os.environ.get("MODAL_TOKEN_ID")
MODAL_TOKEN_SECRET = os.environ.get("MODAL_TOKEN_SECRET")
ENABLE_STARTUP_WIPE = os.environ.get("ENABLE_STARTUP_WIPE", "false").lower() == "true"
SESSION_RETENTION_LIMIT = int(os.environ.get("SESSION_RETENTION_LIMIT", "5"))

# Predator Directives
BASE_DIR = Path(r"D:\V4_SOVEREIGN_MAGIC")
BRAIN_DROP = BASE_DIR / "DROP_ZONE"
EXPORT_ZONE = BASE_DIR / "MD_EXPORTS"
INTERNAL_DIR = BASE_DIR / "INTERNAL"
CACHE_DIR = INTERNAL_DIR / "CACHE"
ERRORS_DIR = INTERNAL_DIR / "ERRORS"

# --- INITIALIZATION ---
def boot_audit():
    for d in [BRAIN_DROP, EXPORT_ZONE, CACHE_DIR, ERRORS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    if not all([SUPABASE_URL, SUPABASE_KEY, MODAL_API_KEY]):
        print("CRITICAL: Missing credentials in .env")
        sys.exit(1)
    
    if MODAL_TOKEN_ID:
        print(f"AUTH_BRIDGE: Token detected ({MODAL_TOKEN_ID[:5]}...).")
    print("V5_APEX_AUDIT: PASS | NEURAL_MAP: READY")

boot_audit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CLOUD PREDATOR LINKAGE (V5 APEX ANALYST) ---
class PredatorCloudEngine:
    def __init__(self):
        try:
            # Linking to the V5 Cloud Class
            self.shredder_cls = modal.Cls.from_name("v4-predator-shredder", "PredatorShredder")
            self.shredder = self.shredder_cls()
        except Exception as e:
            print(f"CLOUD_LINK_ERROR: {e}")
            self.shredder = None

    def process_file(self, file_path: Path):
        print(f"APEX_SHRED: {file_path.name}")
        try:
            file_bytes = file_path.read_bytes()
            doc_hash = hashlib.sha256(file_bytes).hexdigest()
            
            # Collision Check
            existing = supabase.table("v4_vault").select("id").eq("doc_hash", doc_hash).execute()
            if existing.data:
                print(f"GHOST_TRACE: {file_path.name} already in memory. Skipping.")
                return

            if not self.shredder:
                raise ConnectionError("Apex Engine unreachable.")
            
            print(f"SHREDDING IN CLOUD (V5 APEX PROTOCOL)...")
            md_content = self.shredder.shred_and_tag.remote(file_bytes, file_path.name)
            
            import subprocess
            export_path = EXPORT_ZONE / f"{file_path.stem}.md"
            export_path.write_text(md_content, encoding="utf-8")
            print(f"APEX_SUCCESS: {file_path.name} integrated into Neural Map.")

            # Trigger Neural Handshake (Local Sync)
            print("🔄 TRIGGERING NEURAL HANDSHAKE (Auto-Sync)...")
            subprocess.run([sys.executable, str(BASE_DIR / "CODE" / "vault_sync.py"), "--sync-all"], check=False)

        except Exception as e:
            print(f"APEX_FAILURE: {e}")
            target_err = ERRORS_DIR / file_path.name
            try: file_path.rename(target_err)
            except: pass

engine = PredatorCloudEngine()

# --- NATIVE WATCHER ---
class PredatorHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(".pdf"):
            print(f"\nAPEX_TRIGGER: Detecting {Path(event.src_path).name}...")
            engine.process_file(Path(event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"DETECTION: Removing {Path(event.src_path).name} from Neural Map...")
            scan_and_wipe()

def scan_and_wipe():
    print("NEURAL_WIPE: Syncing Cloud Vault with Drop Zone...")
    try:
        local_files = {f.name for f in BRAIN_DROP.glob("*.pdf")}
        res = supabase.table("v4_vault").select("id, filename").execute()
        db_files = res.data or []
        
        for row in db_files:
            if row['filename'] not in local_files:
                filename = row['filename']
                doc_id = row['id']
                print(f"SUPABASE_PURGE: Scrubbing {filename} (Neural Map Cleanse)...")
                
                # 1. Clean local export
                md_filename = filename.rsplit('.', 1)[0] + ".md"
                md_path = EXPORT_ZONE / md_filename
                if md_path.exists():
                    print(f"  🗑️ Removing local export: {md_filename}")
                    md_path.unlink()

                # 2. Explicit delete from graph (cascade handled)
                try: supabase.table("v4_graph").delete().eq("doc_id", doc_id).execute()
                except: pass
                supabase.table("v4_vault").delete().eq("id", doc_id).execute()
        
        print("MEMORY_SOVEREIGNTY: VERIFIED")

        # Trigger Neural Handshake (Local Sync to remove from Kilo/OpenCode)
        import subprocess
        print("🔄 TRIGGERING NEURAL HANDSHAKE (Auto-Sync)...")
        subprocess.run([sys.executable, str(BASE_DIR / "CODE" / "vault_sync.py"), "--sync-all"], check=False)

    except Exception as e:
        print(f"WIPE_ERROR: {e}")

def enforce_retention_policy():
    print(f"APEX_POLICY: Enforcing rolling retention ({SESSION_RETENTION_LIMIT} sessions)...")
    try:
        # 1. Get all unique document filenames ordered by newest first
        res = supabase.table("v4_vault").select("filename, id").order("id", desc=True).execute()
        all_data = res.data or []
        
        unique_files = []
        seen = set()
        for row in all_data:
            fname = row.get('filename')
            if fname and fname not in seen:
                unique_files.append(fname)
                seen.add(fname)
        
        # 2. Identify files to purge
        if len(unique_files) > SESSION_RETENTION_LIMIT:
            to_keep = set(unique_files[:SESSION_RETENTION_LIMIT])
            to_purge = unique_files[SESSION_RETENTION_LIMIT:]
            print(f"  🗑️ Purging {len(to_purge)} older sessions to stay within limit...")
            
            for filename in to_purge:
                print(f"  🔥 Scrubbing: {filename}")
                # Get ID for filename 
                doc_res = supabase.table("v4_vault").select("id").eq("filename", filename).execute()
                if doc_res.data:
                    doc_id = doc_res.data[0]['id']
                    # Clean graph
                    try: supabase.table("v4_graph").delete().eq("doc_id", doc_id).execute()
                    except: pass
                    # Clean vault
                    supabase.table("v4_vault").delete().eq("filename", filename).execute()
                    
                    # Clean local export
                    md_filename = filename.rsplit('.', 1)[0] + ".md"
                    md_path = EXPORT_ZONE / md_filename
                    if md_path.exists():
                        print(f"  🗑️ Removing local export: {md_filename}")
                        md_path.unlink()
            
            print("MEMORY_SOVEREIGNTY: POLICY ENFORCED")
            # Trigger sync to update Kilo/OpenCode
            import subprocess
            subprocess.run([sys.executable, str(BASE_DIR / "CODE" / "vault_sync.py"), "--sync-all"], check=False)
        else:
            print(f"System Load: NOMINAL ({len(unique_files)}/5 sessions active)")
            
    except Exception as e:
        print(f"POLICY_ERROR: {e}")

def main():
    print("--- V5_SOVEREIGN_MAGIC: APEX PROTOCOL ACTIVE ---")
    print(f"Neural Map Monitoring: {BRAIN_DROP}")
    
    # 1. Boot Sync
    if ENABLE_STARTUP_WIPE:
        print("APEX_PURGE: Startup wipe enabled. Syncing...")
        scan_and_wipe()
    else:
        print("APEX_PURGE: Startup wipe disabled. Preserving cloud sessions.")
    
    # 2. Enforce Retention
    enforce_retention_policy()
    
    for f in BRAIN_DROP.glob("*.pdf"):
        engine.process_file(f)

    # 2. Start Watcher
    event_handler = PredatorHandler()
    observer = Observer()
    observer.schedule(event_handler, str(BRAIN_DROP), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
