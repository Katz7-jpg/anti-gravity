import os
import modal

app = modal.App("v5-migration")
image = modal.Image.debian_slim().pip_install("psycopg2-binary")

@app.function(image=image, secrets=[modal.Secret.from_name("v4-predator-secrets")])
def run_migration():
    import psycopg2
    SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    
    # Extract project ref from URL
    project_ref = SUPABASE_URL.split("//")[1].split(".")[0]
    
    # Try different port and user format
    conn_string = f"postgresql://postgres.{project_ref}:{SUPABASE_SERVICE_KEY}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
    
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

    CREATE INDEX IF NOT EXISTS idx_v4_graph_subject ON v4_graph(subject);
    CREATE INDEX IF NOT EXISTS idx_v4_graph_object ON v4_graph(object);
    CREATE INDEX IF NOT EXISTS idx_v4_graph_doc_id ON v4_graph(doc_id);
    """
    
    print(f"Connecting to {project_ref}...")
    try:
        conn = psycopg2.connect(conn_string)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(sql)
        print("MIGRATION_SUCCESS: v4_graph created.")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"MIGRATION_FAILURE: {e}")
        return False
