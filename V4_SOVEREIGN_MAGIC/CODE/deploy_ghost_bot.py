"""
V5 Ghost Bot Deployment Script
Run this script to deploy the bot and register the webhook with Telegram.
"""
import os
import sys
import subprocess
from dotenv import load_dotenv
import requests

# Fix Windows console encoding for emoji/unicode characters
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv(r"d:\AI_FACTORY\.env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def deploy_to_modal():
    """Deploy the bot to Modal."""
    print("=" * 60)
    print("DEPLOYING V5 GHOST BOT TO MODAL...")
    print("=" * 60)
    
    # Set UTF-8 encoding for the subprocess
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(
        ["modal", "deploy", "V5_GHOST_BOT.py"],
        cwd=r"D:\V4_SOVEREIGN_MAGIC\CODE",
        capture_output=True,
        text=True,
        env=env
    )
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode != 0:
        print("DEPLOYMENT FAILED!")
        return None
    
    # Extract webhook URL from output
    for line in result.stdout.split('\n'):
        if 'modal.run' in line and 'https://' in line:
            # Extract URL
            import re
            match = re.search(r'https://[^\s]+\.modal\.run', line)
            if match:
                return match.group(0)
    
    return None

def set_telegram_webhook(webhook_url: str):
    """Register the webhook URL with Telegram."""
    print("\n" + "=" * 60)
    print("REGISTERING WEBHOOK WITH TELEGRAM...")
    print("=" * 60)
    
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        json={"url": webhook_url}
    )
    
    result = response.json()
    print(f"Webhook URL: {webhook_url}")
    print(f"Response: {result}")
    
    if result.get('ok'):
        print("\n✅ WEBHOOK REGISTERED SUCCESSFULLY!")
    else:
        print(f"\n❌ FAILED TO REGISTER WEBHOOK: {result.get('description')}")
    
    return result.get('ok', False)

def verify_webhook():
    """Verify the webhook is properly set."""
    print("\n" + "=" * 60)
    print("VERIFYING WEBHOOK STATUS...")
    print("=" * 60)
    
    response = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    )
    
    result = response.json()
    if result.get('ok'):
        info = result['result']
        print(f"Webhook URL: {info.get('url', 'NOT SET')}")
        print(f"Pending Updates: {info.get('pending_update_count', 0)}")
        print(f"Max Connections: {info.get('max_connections', 'N/A')}")
        
        if info.get('url'):
            print("\n✅ WEBHOOK IS ACTIVE!")
            return True
        else:
            print("\n❌ WEBHOOK IS NOT SET!")
            return False
    
    return False

def main():
    print("\n🦾 V5 GHOST BOT DEPLOYMENT UTILITY")
    print("=" * 60)
    
    # Step 1: Deploy to Modal
    webhook_url = deploy_to_modal()
    
    if not webhook_url:
        print("\n⚠️ Could not extract webhook URL from deployment output.")
        print("Attempting to verify existing webhook...")
        verify_webhook()
        return
    
    print(f"\n✅ DEPLOYED SUCCESSFULLY!")
    print(f"Webhook URL: {webhook_url}")
    
    # Step 2: Register webhook with Telegram
    if set_telegram_webhook(webhook_url):
        # Step 3: Verify
        verify_webhook()
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE!")
    print("=" * 60)
    print("\nTest your bot by sending /start to @Doclingbot on Telegram")

if __name__ == "__main__":
    main()
