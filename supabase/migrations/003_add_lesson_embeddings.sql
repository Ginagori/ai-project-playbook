-- Migration: Add pgvector embeddings to lessons_learned
-- Run this in Supabase SQL Editor
-- Prerequisite: PRP-10 (Semantic search for lessons)

-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Add embedding column (512 dims — unified across OpenAI/Voyage/local backends)
ALTER TABLE lessons_learned
ADD COLUMN IF NOT EXISTS embedding vector(512);

-- Step 3: Create IVFFlat index for fast cosine similarity search
-- lists=10 is appropriate for <1000 rows; increase if lesson count grows past 1000
CREATE INDEX IF NOT EXISTS idx_lessons_embedding
ON lessons_learned USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

-- Step 4: RPC function for semantic similarity search
CREATE OR REPLACE FUNCTION match_lessons(
    query_embedding vector(512),
    match_team_id UUID,
    match_threshold FLOAT DEFAULT 0.3,
    match_count INT DEFAULT 15
)
RETURNS TABLE (
    id UUID,
    category TEXT,
    title TEXT,
    description TEXT,
    context TEXT,
    recommendation TEXT,
    confidence FLOAT,
    frequency INTEGER,
    project_types TEXT[],
    tech_stacks TEXT[],
    tags TEXT[],
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        l.id,
        l.category,
        l.title,
        l.description,
        l.context,
        l.recommendation,
        l.confidence::FLOAT,
        l.frequency,
        l.project_types,
        l.tech_stacks,
        l.tags,
        (1 - (l.embedding <=> query_embedding))::FLOAT AS similarity
    FROM lessons_learned l
    WHERE l.team_id = match_team_id
      AND l.embedding IS NOT NULL
      AND 1 - (l.embedding <=> query_embedding) > match_threshold
    ORDER BY l.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Documentation
COMMENT ON COLUMN lessons_learned.embedding IS 'Semantic embedding vector (512 dims) for similarity search';
COMMENT ON FUNCTION match_lessons IS 'Semantic similarity search for lessons using cosine distance';
