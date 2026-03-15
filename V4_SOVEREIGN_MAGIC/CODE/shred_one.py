import os
import sys
from pathlib import Path
import modal

# --- CONFIGURATION ---
DEFAULT_PATH = Path(r"D:\V4_SOVEREIGN_MAGIC\DROP_ZONE\2030.pdf")

def run_apex_shred(target_path: Path):
    if not target_path.exists():
        print(f"ERROR: {target_path} not found.")
        return

    print(f"[APEX] Manual Trigger: Shredding {target_path.name}...")
    
    try:
        # Link to the deployed V5 Apex Engine
        # We use the shredder from v4-predator-shredder app
        shredder_cls = modal.Cls.from_name("v4-predator-shredder", "PredatorShredder")
        shredder = shredder_cls()
        
        file_bytes = target_path.read_bytes()
        
        # Execute Remote Ingestion
        print(f"Executing Remote Apex Protocol (GLM-5) for {target_path.name}...")
        md_content = shredder.shred_and_tag.remote(file_bytes, target_path.name)
        
        print("\n" + "="*50)
        print("   APEX_PROTOCOL_SUCCESS: SHREDDING COMPLETE")
        print("="*50)
        print(f"Content Sample: {md_content[:300]}...")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    run_apex_shred(path)
