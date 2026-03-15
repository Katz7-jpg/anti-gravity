-- ============================================================================
-- V4_SOVEREIGN_MAGIC - Phase 1 RAG Upgrades Migration
-- Version: 1.1.0
-- Created: 2026-03-05
-- Updated: 2026-03-05 - Changed to 384 dimensions for sentence-transformers
-- Description: Adds pgvector support, embeddings table, prompt cache, and RPC functions
-- ============================================================================

-- ============================================================================
-- STEP 1: Enable pgvector Extension
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- STEP 2: Create v4_embeddings Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS v4_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_id UUID REFERENCES v4_vault(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(384),  -- sentence-transformers all-MiniLM-L6-v2 dimension
    content_hash TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create vector index for similarity search (IVFFlat for approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_v4_embeddings_vector 
ON v4_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for doc_id lookups
CREATE INDEX IF NOT EXISTS idx_v4_embeddings_doc_id ON v4_embeddings(doc_id);

-- Enable Row Level Security
ALTER TABLE v4_embeddings ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- STEP 3: Create prompt_cache Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS prompt_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_hash TEXT UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    context_hash TEXT,
    model_version TEXT DEFAULT 'glm-5',
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days'
);

-- Index for fast cache lookups
CREATE INDEX IF NOT EXISTS idx_prompt_cache_hash ON prompt_cache(query_hash);

-- Index for expiration cleanup
CREATE INDEX IF NOT EXISTS idx_prompt_cache_expires ON prompt_cache(expires_at);

-- Enable Row Level Security
ALTER TABLE prompt_cache ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- STEP 4: Add Columns to v4_vault Table
-- ============================================================================

-- Add embedding reference column (optional link to embeddings)
ALTER TABLE v4_vault 
ADD COLUMN IF NOT EXISTS embedding_id UUID REFERENCES v4_embeddings(id);

-- Add content hash for cache invalidation
ALTER TABLE v4_vault 
ADD COLUMN IF NOT EXISTS content_hash TEXT;

-- ============================================================================
-- STEP 5: Create match_embeddings RPC Function
-- ============================================================================

CREATE OR REPLACE FUNCTION match_embeddings(
    query_embedding VECTOR(384),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    doc_id UUID,
    chunk_index INTEGER,
    similarity FLOAT,
    content TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.id,
        e.doc_id,
        e.chunk_index,
        1 - (e.embedding <=> query_embedding) AS similarity,
        v.content
    FROM v4_embeddings e
    JOIN v4_vault v ON v.id = e.doc_id
    WHERE 1 - (e.embedding <=> query_embedding) > match_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ============================================================================
-- STEP 6: Create Helper Functions
-- ============================================================================

-- Function to clear expired cache entries
CREATE OR REPLACE FUNCTION clear_expired_cache()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM prompt_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- Function to get cache statistics
CREATE OR REPLACE FUNCTION get_cache_stats()
RETURNS TABLE (
    total_entries BIGINT,
    total_hits BIGINT,
    avg_hit_count NUMERIC,
    oldest_entry TIMESTAMPTZ,
    newest_entry TIMESTAMPTZ
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT AS total_entries,
        COALESCE(SUM(hit_count), 0)::BIGINT AS total_hits,
        COALESCE(AVG(hit_count), 0)::NUMERIC AS avg_hit_count,
        MIN(created_at) AS oldest_entry,
        MAX(created_at) AS newest_entry
    FROM prompt_cache;
END;
$$;

-- Function to get embedding statistics
CREATE OR REPLACE FUNCTION get_embedding_stats()
RETURNS TABLE (
    total_embeddings BIGINT,
    unique_documents BIGINT,
    avg_chunk_count NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::BIGINT AS total_embeddings,
        COUNT(DISTINCT doc_id)::BIGINT AS unique_documents,
        CASE 
            WHEN COUNT(DISTINCT doc_id) > 0 
            THEN COUNT(*)::NUMERIC / COUNT(DISTINCT doc_id)::NUMERIC
            ELSE 0 
        END AS avg_chunk_count
    FROM v4_embeddings;
END;
$$;

-- ============================================================================
-- STEP 7: Create Triggers for Auto-Cleanup
-- ============================================================================

-- Trigger to clean expired cache on insert (runs occasionally)
CREATE OR REPLACE FUNCTION maybe_clean_cache()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- 1% chance to clean expired cache on each insert
    IF random() < 0.01 THEN
        PERFORM clear_expired_cache();
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trigger_clean_cache ON prompt_cache;
CREATE TRIGGER trigger_clean_cache
    AFTER INSERT ON prompt_cache
    FOR EACH ROW
    EXECUTE FUNCTION maybe_clean_cache();

-- ============================================================================
-- STEP 8: Grant Permissions (adjust as needed for your Supabase setup)
-- ============================================================================

-- Grant usage on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- Grant table permissions
GRANT ALL ON v4_embeddings TO authenticated;
GRANT ALL ON v4_embeddings TO service_role;

GRANT ALL ON prompt_cache TO authenticated;
GRANT ALL ON prompt_cache TO service_role;

-- Grant function permissions
GRANT EXECUTE ON FUNCTION match_embeddings TO authenticated;
GRANT EXECUTE ON FUNCTION match_embeddings TO service_role;

GRANT EXECUTE ON FUNCTION clear_expired_cache TO authenticated;
GRANT EXECUTE ON FUNCTION clear_expired_cache TO service_role;

GRANT EXECUTE ON FUNCTION get_cache_stats TO authenticated;
GRANT EXECUTE ON FUNCTION get_cache_stats TO service_role;

GRANT EXECUTE ON FUNCTION get_embedding_stats TO authenticated;
GRANT EXECUTE ON FUNCTION get_embedding_stats TO service_role;

-- ============================================================================
-- VERIFICATION QUERIES (Run these to verify installation)
-- ============================================================================

-- Check pgvector extension is installed
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- Check tables exist
-- SELECT table_name FROM information_schema.tables WHERE table_name IN ('v4_embeddings', 'prompt_cache');

-- Check RPC function exists
-- SELECT routine_name FROM information_schema.routines WHERE routine_name = 'match_embeddings';

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
