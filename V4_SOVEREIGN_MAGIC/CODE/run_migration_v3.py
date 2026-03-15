"""
V4 SOVEREIGN MAGIC - SQL Migration via Supabase Management API
Uses the Supabase Management API to execute SQL statements.

Usage:
    python run_migration_v3.py
"""
import os
import sys
import requests
import json
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(r"d:\AI_FACTORY\.env")
except ImportError:
    pass

# Configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ukqycwqzopyxbhkiaorr.supabase.co")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
PROJECT_REF = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")

if not SUPABASE_SERVICE_ROLE_KEY:
    print("ERROR: SUPABASE_SERVICE_ROLE_KEY not found in environment")
    sys.exit(1)

# Migration file path
MIGRATION_FILE = Path(__file__).parent.parent / "supabase" / "migrations" / "phase1_embeddings.sql"

def get_rest_headers():
    """Headers for REST API calls."""
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists via REST API."""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?select=count",
            headers=get_rest_headers(),
            params={"select": "count"}
        )
        return response.status_code == 200
    except Exception:
        return False

def execute_sql_via_internal_endpoint(sql: str) -> tuple[bool, str]:
    """
    Execute SQL via Supabase internal SQL endpoint.
    This uses the /rest/v1/rpc endpoint with a custom function.
    """
    headers = get_rest_headers()
    
    # Method 1: Try exec_sql RPC (if it exists)
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"query": sql}
        )
        if response.status_code == 200:
            return True, "exec_sql RPC"
    except Exception:
        pass
    
    # Method 2: Try pg_net extension (if available)
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/pg_net_http_post",
            headers=headers,
            json={}
        )
    except Exception:
        pass
    
    return False, "No SQL execution method available"

def create_table_via_rest(table_name: str, table_sql: str) -> bool:
    """
    Create a table by inserting a record (workaround for REST API).
    This won't work for DDL statements.
    """
    return False

def run_migration():
    """Run the migration using available methods."""
    print("=" * 60)
    print("V4 SOVEREIGN MAGIC - SQL Migration Runner v3")
    print("=" * 60)
    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"Project Ref: {PROJECT_REF}")
    print(f"Migration File: {MIGRATION_FILE}")
    
    # Read SQL
    with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"\n📄 SQL file loaded: {len(sql)} characters")
    
    # Check current state
    print("\n🔍 Checking current database state...")
    embeddings_exists = check_table_exists("v4_embeddings")
    cache_exists = check_table_exists("prompt_cache")
    
    print(f"  v4_embeddings table: {'✅ EXISTS' if embeddings_exists else '❌ NOT FOUND'}")
    print(f"  prompt_cache table: {'✅ EXISTS' if cache_exists else '❌ NOT FOUND'}")
    
    if embeddings_exists and cache_exists:
        print("\n✅ All tables already exist! Migration not needed.")
        return True
    
    # Try SQL execution
    print("\n🔄 Attempting SQL execution...")
    success, method = execute_sql_via_internal_endpoint(sql)
    
    if success:
        print(f"✅ SQL executed via {method}")
        return True
    
    # If we get here, we need manual intervention
    print("\n" + "=" * 60)
    print("⚠️ AUTOMATIC MIGRATION NOT POSSIBLE")
    print("=" * 60)
    print("\nThe Supabase REST API does not support direct SQL execution.")
    print("You need to run the migration manually in the Supabase Dashboard.")
    print("\n" + "-" * 60)
    print("MANUAL MIGRATION STEPS:")
    print("-" * 60)
    print("\n1. Open Supabase SQL Editor:")
    print(f"   https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new")
    print("\n2. Copy the SQL below and paste it into the editor:")
    print("\n" + "=" * 60)
    print(sql)
    print("=" * 60)
    print("\n3. Click 'Run' to execute the migration")
    print("\n" + "-" * 60)
    
    return False

def test_bot_webhook():
    """Test the bot webhook."""
    print("\n" + "=" * 60)
    print("TESTING BOT WEBHOOK")
    print("=" * 60)
    
    webhook_url = "https://alikhanvro83--v5-apex-ghost-bot-webhook.modal.run"
    
    # Test GET request
    try:
        response = requests.get(webhook_url, timeout=10)
        print(f"\nGET {webhook_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"GET request failed: {e}")
    
    # Test POST request (Telegram style)
    try:
        test_update = {
            "update_id": 0,
            "message": {
                "message_id": 0,
                "from": {"id": 0, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 0, "type": "private"},
                "date": 0,
                "text": "/start"
            }
        }
        response = requests.post(webhook_url, json=test_update, timeout=30)
        print(f"\nPOST {webhook_url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"POST request failed: {e}")

def main():
    # Run migration
    migration_success = run_migration()
    
    # Test webhook
    test_bot_webhook()
    
    # Final status
    print("\n" + "=" * 60)
    if migration_success:
        print("✅ MIGRATION COMPLETE - BOT READY FOR TESTING")
    else:
        print("⚠️ MANUAL MIGRATION REQUIRED")
        print("\nAfter running the SQL manually, the bot will be fully operational.")
    print("=" * 60)
    print("\n📱 Test the bot on Telegram: @Doclingbot")

if __name__ == "__main__":
    main()
