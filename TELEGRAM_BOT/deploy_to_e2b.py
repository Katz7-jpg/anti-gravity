"""
Telegram Bot - E2B Sandbox Deployment Script
==============================================
Deploys the Telegram bot to E2B sandbox to bypass local ISP restrictions.

This script:
1. Connects to E2B sandbox
2. Uploads telegram_bot_e2b.py and requirements.txt
3. Installs dependencies in the sandbox
4. Injects environment variables from .env
5. Runs the bot in the cloud

Usage:
    python TELEGRAM_BOT/deploy_to_e2b.py

Updated for E2B SDK v0.17.0+ compatibility.
"""

import os
import sys
import time
from pathlib import Path

# Fix Windows console encoding for emoji
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARNING] python-dotenv not installed, using system env vars")


def print_banner():
    """Print deployment banner"""
    print()
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║     CLOUD SCOUT DEPLOYMENT - E2B SANDBOX v0.17.0+         ║")
    print("║     Bypass Local ISP Restrictions                         ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print()


def get_credentials():
    """Get credentials from environment variables"""
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    return {
        "telegram_token": telegram_token,
        "supabase_url": supabase_url,
        "supabase_key": supabase_key
    }


def validate_credentials(creds):
    """Validate that all required credentials are present"""
    missing = []
    
    if not creds["telegram_token"]:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not creds["supabase_url"]:
        missing.append("SUPABASE_URL")
    if not creds["supabase_key"]:
        missing.append("SUPABASE_SERVICE_ROLE_KEY")
    
    if missing:
        print(f"[ERROR] Missing credentials in .env:")
        for var in missing:
            print(f"  - {var}")
        return False
    
    return True


def read_local_files():
    """Read the bot files to upload"""
    base_path = Path(__file__).parent
    
    # Read telegram_bot_e2b.py
    bot_file = base_path / "telegram_bot_e2b.py"
    if not bot_file.exists():
        print(f"[ERROR] Bot file not found: {bot_file}")
        return None, None
    
    with open(bot_file, "r", encoding="utf-8") as f:
        bot_code = f.read()
    
    # Read requirements.txt from project root
    requirements_file = base_path.parent / "requirements.txt"
    if not requirements_file.exists():
        print(f"[WARNING] requirements.txt not found at {requirements_file}")
        # Create minimal requirements
        requirements = "requests>=2.31.0\npython-dotenv>=1.0.0\n"
    else:
        with open(requirements_file, "r", encoding="utf-8") as f:
            requirements = f.read()
    
    return bot_code, requirements


def deploy_telegram_scout():
    """Deploy Telegram bot to E2B sandbox using v0.17.0+ SDK"""
    
    print_banner()
    
    # Step 1: Validate credentials
    print("[1/6] Validating credentials...")
    creds = get_credentials()
    if not validate_credentials(creds):
        return {"status": "error", "message": "Missing credentials"}
    print("  ✅ All credentials present")
    
    # Step 2: Read local files
    print("[2/6] Reading local files...")
    bot_code, requirements = read_local_files()
    if bot_code is None:
        return {"status": "error", "message": "Bot file not found"}
    print("  ✅ Files read successfully")
    
    # Step 3: Create E2B Sandbox (v0.17.0+ API)
    print("[3/6] Creating E2B Sandbox...")
    try:
        from e2b import Sandbox
        
        # v0.17.0+ SDK - use Sandbox.create() with template parameter
        sbx = Sandbox.create(template="base")
        print(f"  ✅ Sandbox created: {sbx.sandbox_id}")
    except ImportError as e:
        print(f"[ERROR] E2B not installed correctly: {e}")
        print("[FIX] Run: pip install e2b --upgrade")
        return {"status": "error", "message": f"E2B import error: {e}"}
    except Exception as e:
        print(f"  ❌ Failed to create sandbox: {e}")
        return {"status": "error", "message": str(e)}
    
    # Step 4: Upload files
    print("[4/6] Uploading bot files...")
    try:
        # Upload bot code
        sbx.files.write("/home/user/telegram_bot.py", bot_code)
        print("  ✅ Uploaded telegram_bot.py")
        
        # Upload requirements
        sbx.files.write("/home/user/requirements.txt", requirements)
        print("  ✅ Uploaded requirements.txt")
    except Exception as e:
        print(f"  ❌ Failed to upload files: {e}")
        return {"status": "error", "message": str(e)}
    
    # Step 5: Install dependencies (v0.17.0+ API - use commands.run)
    print("[5/6] Installing dependencies...")
    try:
        # v0.17.0+ SDK - use sbx.commands.run() instead of sbx.process.run()
        result = sbx.commands.run("pip install python-telegram-bot supabase python-dotenv")
        print("  ✅ Dependencies installed")
    except Exception as e:
        print(f"  ⚠️ Dependency installation warning: {e}")
    
    # Step 6: Start the bot with environment variables
    print("[6/6] Starting Telegram Scout...")
    
    # Build environment setup command
    env_setup = f"export TELEGRAM_BOT_TOKEN='{creds['telegram_token']}' && "
    env_setup += f"export SUPABASE_URL='{creds['supabase_url']}' && "
    env_setup += f"export SUPABASE_SERVICE_ROLE_KEY='{creds['supabase_key']}'"
    
    # Print deployment info
    print()
    print("  ═══════════════════════════════════════════════════════════")
    print("   ✅ SCOUT IS LIVE IN E2B CLOUD")
    print(f"   Sandbox ID: {sbx.sandbox_id}")
    print("   📱 Check your iPhone for the /start response")
    print("   Bot is running in background")
    print("  ═══════════════════════════════════════════════════════════")
    print()
    
    try:
        # v0.17.0+ SDK - use commands.run with background=True
        # Explicitly call python for the bot script
        sbx.commands.run(
            f"{env_setup} && python /home/user/telegram_bot.py",
            background=True
        )
        
        print("Press Ctrl+C to stop the deployment...")
        try:
            while True:
                time.sleep(60)
                print(f"[ALIVE] Sandbox {sbx.sandbox_id[:8]}... still running")
        except KeyboardInterrupt:
            print("\n[STOP] Closing sandbox...")
            sbx.close()
            print("[DONE] Sandbox closed.")
        
        return {
            "status": "success",
            "sandbox_id": sbx.sandbox_id
        }
        
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    result = deploy_telegram_scout()
    
    print()
    print("=" * 60)
    print("DEPLOYMENT RESULT")
    print("=" * 60)
    print(f"Status: {result.get('status', 'unknown')}")
    
    if result.get('status') == 'success':
        print(f"Sandbox ID: {result.get('sandbox_id', 'N/A')}")
        print()
        print("✅ Cloud Scout deployment completed!")
    else:
        print(f"Message: {result.get('message', 'Unknown error')}")
        print()
        print("❌ Cloud Scout deployment failed!")
        sys.exit(1)
