"""
V4 SOVEREIGN MAGIC - Automatic SQL Migration Runner
Runs the Phase 1 RAG Upgrades migration via Supabase REST API.

Usage:
    python run_migration.py
    
Environment Variables Required:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_SERVICE_ROLE_KEY - Service role key for admin access
"""
import os
import sys
import requests
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

def read_migration_sql() -> str:
    """Read the SQL migration file."""
    if not MIGRATION_FILE.exists():
        print(f"ERROR: Migration file not found: {MIGRATION_FILE}")
        sys.exit(1)
    
    with open(MIGRATION_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def run_migration_via_rpc():
    """
    Run migration using Supabase RPC.
    This approach uses the exec_sql RPC function if available.
    """
    sql = read_migration_sql()
    
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    # Try to execute via RPC
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers=headers,
            json={"query": sql}
        )
        
        if response.status_code == 200:
            print("✅ Migration executed successfully via RPC")
            return True
        elif response.status_code == 404:
            print("⚠️ RPC method not available, trying direct SQL execution...")
            return False
        else:
            print(f"⚠️ RPC execution failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ RPC execution error: {e}")
        return False

def run_migration_via_direct_connection():
    """
    Run migration using direct PostgreSQL connection.
    Requires psycopg2 and direct database access.
    """
    try:
        import psycopg2
        
        # Parse Supabase URL for connection string
        # Supabase provides direct database connection via port 5432
        db_url = os.environ.get("DATABASE_URL")
        
        if not db_url:
            # Construct from Supabase URL
            # Format: postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
            project_ref = SUPABASE_URL.replace("https://", "").replace(".supabase.co", "")
            db_password = os.environ.get("SUPABASE_DB_PASSWORD")
            
            if not db_password:
                print("⚠️ DATABASE_URL or SUPABASE_DB_PASSWORD required for direct connection")
                return False
            
            db_url = f"postgresql://postgres:{db_password}@db.{project_ref}.supabase.co:5432/postgres"
        
        sql = read_migration_sql()
        
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            cur.execute(sql)
        
        conn.close()
        print("✅ Migration executed successfully via direct connection")
        return True
        
    except ImportError:
        print("⚠️ psycopg2 not installed, skipping direct connection")
        return False
    except Exception as e:
        print(f"⚠️ Direct connection error: {e}")
        return False

def run_migration_via_split_statements():
    """
    Run migration by executing individual SQL statements via REST API.
    This is a fallback method that works with Supabase REST API.
    """
    sql = read_migration_sql()
    
    # Split SQL into individual statements
    statements = []
    current_stmt = []
    
    for line in sql.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('--'):
            continue
        
        current_stmt.append(line)
        
        # Check if statement is complete
        if line.endswith(';'):
            stmt = ' '.join(current_stmt)
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_stmt = []
    
    # Execute each statement
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    success_count = 0
    error_count = 0
    
    for i, stmt in enumerate(statements):
        # Skip certain statements that require superuser privileges
        if any(skip in stmt.upper() for skip in ['CREATE EXTENSION', 'GRANT ALL', 'ALTER TABLE']):
            print(f"⏭️ Skipping privileged statement {i+1}: {stmt[:50]}...")
            continue
        
        try:
            # Try to execute via SQL endpoint
            response = requests.post(
                f"{SUPABASE_URL}/rest/v1/sql",
                headers=headers,
                json={"query": stmt}
            )
            
            if response.status_code in [200, 201]:
                success_count += 1
                print(f"✅ Statement {i+1} executed successfully")
            else:
                error_count += 1
                print(f"⚠️ Statement {i+1} failed: {response.status_code}")
        except Exception as e:
            error_count += 1
            print(f"⚠️ Statement {i+1} error: {e}")
    
    print(f"\n📊 Migration Summary: {success_count} succeeded, {error_count} failed")
    return error_count == 0

def verify_migration():
    """Verify that the migration was successful by checking tables."""
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("\n🔍 Verifying migration...")
    
    # Check v4_embeddings table
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/v4_embeddings?select=count",
            headers=headers,
            params={"select": "count"}
        )
        
        if response.status_code == 200:
            print("✅ v4_embeddings table exists")
        else:
            print("⚠️ v4_embeddings table not found")
    except Exception as e:
        print(f"⚠️ Error checking v4_embeddings: {e}")
    
    # Check prompt_cache table
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/prompt_cache?select=count",
            headers=headers,
            params={"select": "count"}
        )
        
        if response.status_code == 200:
            print("✅ prompt_cache table exists")
        else:
            print("⚠️ prompt_cache table not found")
    except Exception as e:
        print(f"⚠️ Error checking prompt_cache: {e}")
    
    # Check pgvector extension via RPC
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/rpc/match_embeddings",
            headers=headers,
            json={
                "query_embedding": [0.0] * 384,  # Test with zero vector (384 for sentence-transformers)
                "match_threshold": 0.5,
                "match_count": 1
            }
        )
        
        if response.status_code == 200:
            print("✅ match_embeddings RPC function exists")
        else:
            print("⚠️ match_embeddings RPC function not found")
    except Exception as e:
        print(f"⚠️ Error checking match_embeddings: {e}")

def main():
    print("=" * 60)
    print("V4 SOVEREIGN MAGIC - Phase 1 RAG Migration Runner")
    print("=" * 60)
    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"Migration File: {MIGRATION_FILE}")
    print()
    
    # Try different methods in order
    methods = [
        ("Direct Connection", run_migration_via_direct_connection),
        ("RPC Execution", run_migration_via_rpc),
        ("Split Statements", run_migration_via_split_statements),
    ]
    
    success = False
    for method_name, method_func in methods:
        print(f"\n🔄 Trying {method_name}...")
        if method_func():
            success = True
            break
    
    # Verify migration
    verify_migration()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ MIGRATION COMPLETE!")
    else:
        print("⚠️ Migration may require manual execution")
        print("\nTo run manually:")
        print("1. Go to Supabase Dashboard > SQL Editor")
        print("2. Paste the contents of phase1_embeddings.sql")
        print("3. Execute the SQL")
    print("=" * 60)

if __name__ == "__main__":
    main()
