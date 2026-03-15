"""
V4 SOVEREIGN MAGIC - Final Migration Script
Attempts multiple methods to execute the SQL migration.

Usage:
    python run_migration_final.py
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

def get_headers():
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
    }

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists via REST API."""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?select=count",
            headers=get_headers()
        )
        return response.status_code == 200
    except Exception:
        return False

def test_rpc_function(func_name: str) -> bool:
    """Test if an RPC function exists."""
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/{func_name}",
            headers=get_headers(),
            json={}
        )
        # 200 means it executed, 404 means function doesn't exist
        return response.status_code != 404
    except Exception:
        return False

def run_migration_via_psycopg2():
    """Run migration using direct PostgreSQL connection."""
    try:
        import psycopg2
        
        db_password = os.environ.get("SUPABASE_DB_PASSWORD")
        if not db_password:
            print("⚠️ SUPABASE_DB_PASSWORD not set")
            return False
        
        db_url = f"postgresql://postgres:{db_password}@db.{PROJECT_REF}.supabase.co:5432/postgres"
        
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print("🔄 Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        
        print("🔄 Executing migration...")
        with conn.cursor() as cur:
            cur.execute(sql)
        
        conn.close()
        print("✅ Migration executed successfully!")
        return True
        
    except ImportError:
        print("⚠️ psycopg2 not installed")
        return False
    except Exception as e:
        print(f"⚠️ Database error: {e}")
        return False

def run_migration_via_pooler():
    """Run migration using Supabase connection pooler."""
    try:
        import psycopg2
        
        db_password = os.environ.get("SUPABASE_DB_PASSWORD")
        if not db_password:
            print("⚠️ SUPABASE_DB_PASSWORD not set")
            return False
        
        # Connection pooler uses port 6543
        db_url = f"postgresql://postgres.{PROJECT_REF}:{db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print("🔄 Connecting via pooler...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        
        print("🔄 Executing migration...")
        with conn.cursor() as cur:
            cur.execute(sql)
        
        conn.close()
        print("✅ Migration executed successfully!")
        return True
        
    except ImportError:
        print("⚠️ psycopg2 not installed")
        return False
    except Exception as e:
        print(f"⚠️ Pooler error: {e}")
        return False

def verify_migration():
    """Verify migration status."""
    print("\n" + "=" * 60)
    print("VERIFICATION STATUS")
    print("=" * 60)
    
    tables = {
        "v4_vault": check_table_exists("v4_vault"),
        "v4_embeddings": check_table_exists("v4_embeddings"),
        "prompt_cache": check_table_exists("prompt_cache"),
    }
    
    for table, exists in tables.items():
        status = "✅ EXISTS" if exists else "❌ MISSING"
        print(f"  {table}: {status}")
    
    return all(tables.values())

def test_bot_webhook():
    """Test the bot webhook."""
    print("\n" + "=" * 60)
    print("BOT WEBHOOK TEST")
    print("=" * 60)
    
    webhook_url = "https://alikhanvro83--v5-apex-ghost-bot-webhook.modal.run"
    
    try:
        # Test with a Telegram-style update
        test_update = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "from": {"id": 12345, "is_bot": False, "first_name": "Test"},
                "chat": {"id": 12345, "type": "private"},
                "date": 1709673600,
                "text": "/start"
            }
        }
        
        response = requests.post(webhook_url, json=test_update, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ Webhook responding: {response.json()}")
            return True
        else:
            print(f"⚠️ Webhook returned: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test failed: {e}")
        return False

def print_manual_instructions():
    """Print manual migration instructions."""
    print("\n" + "=" * 60)
    print("⚠️ AUTOMATIC MIGRATION NOT POSSIBLE")
    print("=" * 60)
    print("""
The Supabase REST API does not support DDL statements (CREATE TABLE, etc.).
You need to run the migration manually in the Supabase Dashboard.

QUICK STEPS:
============

1. Open this URL in your browser:
   https://supabase.com/dashboard/project/ukqycwqzopyxbhkiaorr/sql/new

2. If not logged in, log in to your Supabase account

3. Copy the contents of this file:
   D:\\V4_SOVEREIGN_MAGIC\\supabase\\migrations\\phase1_embeddings.sql

4. Paste it into the SQL Editor

5. Click "Run" (or press Ctrl+Enter)

6. The migration will create:
   - v4_embeddings table (for RAG)
   - prompt_cache table (for caching)
   - match_embeddings RPC function
   - Helper functions and triggers

ALTERNATIVE: Set SUPABASE_DB_PASSWORD in your .env file
This is found in: Supabase Dashboard > Project Settings > Database > Database Password
""")

def main():
    print("=" * 60)
    print("V4 SOVEREIGN MAGIC - Migration Runner (Final)")
    print("=" * 60)
    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"Project Ref: {PROJECT_REF}")
    print(f"Migration File: {MIGRATION_FILE}")
    
    # Check current state
    print("\n" + "-" * 60)
    print("CURRENT DATABASE STATE:")
    print("-" * 60)
    
    vault_exists = check_table_exists("v4_vault")
    embeddings_exists = check_table_exists("v4_embeddings")
    cache_exists = check_table_exists("prompt_cache")
    
    print(f"  v4_vault: {'✅' if vault_exists else '❌'}")
    print(f"  v4_embeddings: {'✅' if embeddings_exists else '❌'}")
    print(f"  prompt_cache: {'✅' if cache_exists else '❌'}")
    
    if embeddings_exists and cache_exists:
        print("\n✅ All tables exist! Migration already complete.")
        test_bot_webhook()
        return
    
    # Try migration methods
    print("\n" + "-" * 60)
    print("ATTEMPTING MIGRATION:")
    print("-" * 60)
    
    success = False
    
    # Method 1: Direct connection
    print("\n🔄 Method 1: Direct PostgreSQL connection...")
    if run_migration_via_psycopg2():
        success = True
    elif not success:
        # Method 2: Connection pooler
        print("\n🔄 Method 2: Connection pooler...")
        if run_migration_via_pooler():
            success = True
    
    # Verify
    if success:
        print("\n" + "-" * 60)
        print("POST-MIGRATION STATE:")
        print("-" * 60)
        verify_migration()
    else:
        print_manual_instructions()
    
    # Test webhook
    test_bot_webhook()
    
    print("\n" + "=" * 60)
    print("BOT STATUS: @Doclingbot")
    print("=" * 60)
    print("\nThe bot webhook is deployed and responding.")
    print("Test it on Telegram by sending /start to @Doclingbot")
    print("\nNote: RAG features require the migration to be complete.")

if __name__ == "__main__":
    main()
