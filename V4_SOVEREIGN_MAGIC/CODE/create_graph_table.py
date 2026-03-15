import os
import psycopg2
from dotenv import load_dotenv

# Load credentials
load_dotenv(r"d:\AI_FACTORY\.env")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_SERVICE_KEY:
    print("CRITICAL: Missing SUPABASE_SERVICE_ROLE_KEY in .env")
    exit(1)

# Connect to Supabase Postgres directly
conn_string = f"postgresql://postgres.ukqycwqzopyxbhkiaorr:{SUPABASE_SERVICE_KEY}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

sql = """
-- V5 APEX PROTOCOL: NEURAL MAP SCHEMA
CREATE TABLE IF NOT EXISTS v4_graph (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID REFERENCES v4_vault(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    relation TEXT NOT NULL,
    object TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast relational lookup (100,000x Speed Prep)
CREATE INDEX IF NOT EXISTS idx_v4_graph_subject ON v4_graph(subject);
CREATE INDEX IF NOT EXISTS idx_v4_graph_object ON v4_graph(object);
CREATE INDEX IF NOT EXISTS idx_v4_graph_doc_id ON v4_graph(doc_id);
"""

try:
    print("[DIRECT] Connecting to Supabase Postgres...")
    conn = psycopg2.connect(conn_string)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("[DIRECT] Executing CREATE TABLE v4_graph...")
    cursor.execute(sql)
    
    print("[SUCCESS] Table v4_graph created successfully!")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"[ERROR] Connection or Execution failed: {e}")
    print("Check if your IP is whitelisted in Supabase if connection times out.")
