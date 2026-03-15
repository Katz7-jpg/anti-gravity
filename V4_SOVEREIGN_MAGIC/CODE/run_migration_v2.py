"""
V4 SOVEREIGN MAGIC - Automatic SQL Migration Runner v2
Uses Supabase Management API to create tables and functions.

Usage:
    python run_migration_v2.py
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

if not SUPABASE_SERVICE_ROLE_KEY:
    print("ERROR: SUPABASE_SERVICE_ROLE_KEY not found in environment")
    sys.exit(1)

# Migration file path
MIGRATION_FILE = Path(__file__).parent.parent / "supabase" / "migrations" / "phase1_embeddings.sql"

def get_headers():
    """Get headers for Supabase REST API."""
    return {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/{table_name}?select=count",
            headers=get_headers(),
            params={"select": "count"}
        )
        return response.status_code == 200
    except Exception:
        return False

def create_table_via_rpc(table_name: str, columns: dict):
    """Create a table using RPC call if available."""
    # This won't work without a custom RPC function
    pass

def execute_sql_via_management_api(sql: str) -> bool:
    """
    Execute SQL via Supabase Management API.
    Note: This requires the project to have SQL execution enabled.
    """
    # Extract project ref from URL
    project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
    
    # Try the internal SQL endpoint (may not be available)
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec",
            headers=get_headers(),
            json={"sql": sql}
        )
        return response.status_code == 200
    except Exception:
        return False

def create_embeddings_table():
    """Create v4_embeddings table using REST API approach."""
    print("\n🔄 Creating v4_embeddings table...")
    
    # Check if table already exists
    if check_table_exists("v4_embeddings"):
        print("✅ v4_embeddings table already exists")
        return True
    
    # We need to use direct SQL for this
    print("⚠️ Cannot create table via REST API - requires SQL execution")
    return False

def create_prompt_cache_table():
    """Create prompt_cache table using REST API approach."""
    print("\n🔄 Creating prompt_cache table...")
    
    # Check if table already exists
    if check_table_exists("prompt_cache"):
        print("✅ prompt_cache table already exists")
        return True
    
    print("⚠️ Cannot create table via REST API - requires SQL execution")
    return False

def run_migration_via_psycopg2():
    """
    Run migration using direct PostgreSQL connection via psycopg2.
    This is the most reliable method.
    """
    try:
        import psycopg2
        
        # Get database password from environment
        db_password = os.environ.get("SUPABASE_DB_PASSWORD")
        
        if not db_password:
            print("⚠️ SUPABASE_DB_PASSWORD not set - trying connection pooling...")
            # Try connection pooling endpoint (port 6543)
            project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
            
            # Try common password patterns or prompt user
            print("\n" + "=" * 60)
            print("DATABASE PASSWORD REQUIRED")
            print("=" * 60)
            print("\nTo run this migration automatically, set SUPABASE_DB_PASSWORD")
            print("in your .env file. You can find this in Supabase Dashboard:")
            print("  Project Settings > Database > Database Password")
            print("\nAlternatively, run the migration manually in Supabase SQL Editor.")
            return False
        
        # Construct connection string
        project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
        db_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
        
        # Read SQL file
        with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        print(f"\n🔄 Connecting to database...")
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
        print(f"⚠️ Database connection error: {e}")
        return False

def verify_migration():
    """Verify that the migration was successful."""
    print("\n🔍 Verifying migration...")
    
    # Check v4_embeddings table
    if check_table_exists("v4_embeddings"):
        print("✅ v4_embeddings table exists")
    else:
        print("⚠️ v4_embeddings table not found")
    
    # Check prompt_cache table
    if check_table_exists("prompt_cache"):
        print("✅ prompt_cache table exists")
    else:
        print("⚠️ prompt_cache table not found")

def test_bot_webhook():
    """Test the deployed bot webhook."""
    print("\n🔍 Testing bot webhook...")
    
    webhook_url = "https://alikhanvro83--v5-apex-ghost-bot-webhook.modal.run"
    
    try:
        response = requests.get(webhook_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ Bot webhook is responding: {response.text[:100]}")
            return True
        else:
            print(f"⚠️ Bot webhook returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Bot webhook test failed: {e}")
        return False

def print_manual_instructions():
    """Print instructions for manual migration."""
    print("\n" + "=" * 60)
    print("MANUAL MIGRATION INSTRUCTIONS")
    print("=" * 60)
    print("\n1. Open Supabase Dashboard:")
    print(f"   https://supabase.com/dashboard/project/ukqycwqzopyxbhkiaorr/sql")
    print("\n2. Click 'SQL Editor' in the left sidebar")
    print("\n3. Click 'New Query'")
    print("\n4. Copy and paste the contents of:")
    print(f"   {MIGRATION_FILE}")
    print("\n5. Click 'Run' to execute the migration")
    print("\n" + "=" * 60)

def main():
    print("=" * 60)
    print("V4 SOVEREIGN MAGIC - Phase 1 RAG Migration Runner v2")
    print("=" * 60)
    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"Migration File: {MIGRATION_FILE}")
    
    # First verify current state
    verify_migration()
    
    # Test bot webhook
    test_bot_webhook()
    
    # Try psycopg2 migration
    print("\n" + "=" * 60)
    print("ATTEMPTING DATABASE MIGRATION")
    print("=" * 60)
    
    success = run_migration_via_psycopg2()
    
    if success:
        # Verify again after migration
        verify_migration()
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
    else:
        print_manual_instructions()
    
    # Test bot webhook again
    test_bot_webhook()

if __name__ == "__main__":
    main()
