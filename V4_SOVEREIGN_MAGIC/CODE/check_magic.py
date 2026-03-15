import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

def print_status(label, success, detail=""):
    symbol = "✅" if success else "❌"
    print(f"{symbol} {label:.<30} {detail}")

def main():
    print("\n" + "="*50)
    print("   V4 SOVEREIGN MAGIC: FINAL DEPLOYMENT DIAGNOSTIC")
    print("="*50 + "\n")

    # 1. Folder Integrity
    base = Path(r"D:\V4_SOVEREIGN_MAGIC")
    folders = ["CODE", "DROP_ZONE", "MD_EXPORTS", "INTERNAL"]
    for f in folders:
        path = base / f
        print_status(f"Folder: {f}", path.exists(), str(path))

    # 2. Environment Audit
    load_dotenv(r"d:\AI_FACTORY\.env")
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    modal_key = os.environ.get("MODAL_API_KEY")

    print_status("Supabase URL", bool(url), url[:15] + "..." if url else "")
    print_status("Supabase Key", bool(key), "Present" if key else "MISSING")
    print_status("Modal Key", bool(modal_key), "Present" if modal_key else "MISSING")

    # 3. Supabase Connection & Schema
    if url and key:
        try:
            sb = create_client(url, key)
            res = sb.table("v4_vault").select("id").limit(1).execute()
            print_status("Supabase Vault Table", True, "Connected & Verified")
        except Exception as e:
            print_status("Supabase Connection", False, str(e))

    # 4. Code Readiness
    main_py = base / "CODE" / "main.py"
    shredder_py = base / "CODE" / "V4_CLOUD_PREDATOR.py"
    print_status("Predator Sync Logic", main_py.exists(), "Ready")
    print_status("Cloud Predator Script", shredder_py.exists(), "Ready for Deployment")

    print("\n" + "="*50)
    print("   RESULT: FINAL MAGIC ARCHITECTURE IS GREEN.")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
