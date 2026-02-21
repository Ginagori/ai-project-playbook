# PRP: Add pgvector Embeddings to Lessons

## Goal
Add vector embeddings to the `lessons_learned` table so that semantic search becomes possible — finding lessons by meaning, not just exact keyword overlap.

## Why
Today, MemoryBridge finds lessons using exact string matching: `tech_stacks.overlaps(["nextjs"])` and `project_types.contains(["saas"])`. This means a lesson about "Supabase RLS multi-tenant isolation" will NOT be found when the context is "database security patterns" — even though they're semantically related. With ~150 lessons, the knowledge base is large enough that keyword matching misses critical connections. Embeddings solve this: they convert each lesson into a 384-dimensional vector where semantically similar lessons are geometrically close. Supabase already supports pgvector natively, and `sentence-transformers` is already in our dependencies (installed but unused).

## What
1. Enable pgvector extension in Supabase and add an `embedding` column to `lessons_learned`
2. Create a Python module that generates embeddings using `sentence-transformers` (local, free, no API key)
3. Create a Supabase RPC function `match_lessons` for cosine similarity search
4. Backfill embeddings for all existing lessons
5. Auto-generate embeddings when new lessons are created

## Success Criteria
- [ ] `lessons_learned.embedding` column exists (vector(384))
- [ ] `match_lessons` RPC returns semantically similar lessons (e.g., query "auth security" finds RLS lessons)
- [ ] All existing lessons (~150) have embeddings
- [ ] New lessons get embeddings on insert (both `playbook_share_lesson` and auto-capture)
- [ ] Embedding generation takes <2s per lesson (local model)
- [ ] System works without embeddings (graceful fallback if model unavailable)

## Context

### Must-Read Files
- `supabase/schema.sql` — current schema, `lessons_learned` table structure
- `supabase/migrations/001_add_repo_url.sql` — migration pattern to follow
- `agent/memory_bridge.py` — `_query_supabase_sync()` is where Supabase queries happen (will be modified in PRP-11)
- `agent/meta_learning/capture.py` — `_sync_lessons_to_supabase()` inserts new lessons
- `mcp_server/playbook_mcp.py` — `playbook_share_lesson` tool inserts lessons via `db.add_lesson()`
- `agent/supabase_client.py` — `add_lesson()` method for Supabase inserts

### Codebase Context
- `sentence-transformers>=2.2.0` is in `requirements.txt` but never used — this PRP activates it
- The model `all-MiniLM-L6-v2` produces 384-dimensional vectors, is ~80MB, fast (~50ms per embedding)
- Supabase Cloud supports pgvector natively — just need to enable the extension
- Current lesson text for embedding = `"{title}. {description}. {recommendation}"` — concatenation of the 3 most semantic fields
- The `_sync_lessons_to_supabase()` function in `capture.py` already has the insert/update pattern

### Known Gotchas
- pgvector extension must be enabled BEFORE adding the column: `CREATE EXTENSION IF NOT EXISTS vector`
- The `vector(384)` type must match the model's output dimension exactly — `all-MiniLM-L6-v2` = 384
- First call to `SentenceTransformer` downloads the model (~80MB) — handle gracefully with try/except
- Supabase `insert()` doesn't accept Python lists for vector columns — must convert to string format `"[0.1, 0.2, ...]"`
- The embedding module should be a singleton to avoid loading the model multiple times
- On machines without GPU (our case), inference is CPU-only — still fast for short text (<100ms)

### Relevant Patterns
- Migration pattern: `supabase/migrations/001_add_repo_url.sql`
- Lesson insert pattern: `agent/meta_learning/capture.py` `_sync_lessons_to_supabase()`
- Singleton pattern: `agent/memory_bridge.py` `MemoryBridge.get_instance()`

## Implementation Blueprint

### Data Models
No new Pydantic models. The embedding is stored in Supabase only (not in local `LessonLearned`).

### Tasks

#### Task 1: SQL migration — enable pgvector and add embedding column
**Files:** `supabase/migrations/003_add_lesson_embeddings.sql`
**Pseudocode:**
```sql
-- Enable pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Add embedding column
ALTER TABLE lessons_learned
ADD COLUMN IF NOT EXISTS embedding vector(384);

-- Create index for fast similarity search (IVFFlat for <1000 rows)
CREATE INDEX IF NOT EXISTS idx_lessons_embedding
ON lessons_learned USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 10);

-- RPC function for semantic search
CREATE OR REPLACE FUNCTION match_lessons(
    query_embedding vector(384),
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
        l.id, l.category, l.title, l.description, l.context,
        l.recommendation, l.confidence, l.frequency,
        l.project_types, l.tech_stacks, l.tags,
        1 - (l.embedding <=> query_embedding) AS similarity
    FROM lessons_learned l
    WHERE l.team_id = match_team_id
      AND l.embedding IS NOT NULL
      AND 1 - (l.embedding <=> query_embedding) > match_threshold
    ORDER BY l.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

#### Task 2: Create embedding generator module
**Files:** `agent/embedding.py` (new file)
**Pseudocode:**
```python
"""Embedding generator for lesson semantic search.

Uses sentence-transformers (already in requirements.txt) with all-MiniLM-L6-v2.
Singleton pattern to avoid loading the model multiple times.
"""
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None

def _get_model() -> SentenceTransformer | None:
    """Load the model (lazy singleton). Returns None if unavailable."""
    global _model
    if _model is None:
        try:
            _model = SentenceTransformer(MODEL_NAME)
        except Exception as e:
            print(f"[Embedding] Failed to load model: {e}")
            return None
    return _model

def generate_lesson_embedding(title: str, description: str, recommendation: str) -> list[float] | None:
    """Generate a 384-dim embedding for a lesson's semantic content."""
    model = _get_model()
    if model is None:
        return None
    text = f"{title}. {description}. {recommendation}"
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def generate_query_embedding(query: str) -> list[float] | None:
    """Generate embedding for a search query."""
    model = _get_model()
    if model is None:
        return None
    embedding = model.encode(query, normalize_embeddings=True)
    return embedding.tolist()
```

#### Task 3: Create backfill script for existing lessons
**Files:** `scripts/backfill_embeddings.py` (new file)
**Depends on:** Task 1, Task 2
**Pseudocode:**
```python
"""Backfill embeddings for all existing Supabase lessons.

Usage:
    .venv/Scripts/python.exe scripts/backfill_embeddings.py [--dry-run]
"""
from agent.embedding import generate_lesson_embedding

def backfill():
    # Connect to Supabase
    # Fetch all lessons WHERE embedding IS NULL
    # For each lesson:
    #   embedding = generate_lesson_embedding(title, description, recommendation)
    #   UPDATE lessons_learned SET embedding = embedding WHERE id = lesson_id
    # Print stats: total, updated, failed
```

#### Task 4: Auto-embed on lesson creation
**Files:** `agent/meta_learning/capture.py`, `agent/supabase_client.py`
**Depends on:** Task 2
**Pseudocode:**
```python
# In _sync_lessons_to_supabase(), after building the data dict:
from agent.embedding import generate_lesson_embedding

embedding = generate_lesson_embedding(lesson.title, lesson.description, lesson.recommendation)
if embedding:
    data["embedding"] = embedding  # Supabase accepts list[float] for vector columns

# In supabase_client.py add_lesson(), same pattern:
# Generate embedding before insert
```

### Integration Points
- **Connects to:** Supabase `lessons_learned` table (new column + RPC), `sentence-transformers` model
- **Called by:** PRP-11 (MemoryBridge semantic search), backfill script, auto-capture, share_lesson
- **Depends on:** pgvector extension enabled in Supabase

## Validation Loop

### Level 1: Syntax & Style
```bash
.venv/Scripts/python.exe -c "
import py_compile
py_compile.compile('agent/embedding.py', doraise=True)
py_compile.compile('scripts/backfill_embeddings.py', doraise=True)
print('Syntax OK')
"
```

### Level 2: Type Safety
```bash
.venv/Scripts/python.exe -c "
from agent.embedding import generate_lesson_embedding, generate_query_embedding
print('Imports OK')
"
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.embedding import generate_lesson_embedding, generate_query_embedding
import numpy as np

# Test lesson embedding
emb = generate_lesson_embedding('Supabase RLS', 'Row level security for multi-tenant', 'Always set RLS from day 1')
assert emb is not None, 'Embedding generation failed'
assert len(emb) == 384, f'Expected 384 dims, got {len(emb)}'
print(f'Lesson embedding: {len(emb)} dims, norm={np.linalg.norm(emb):.3f}')

# Test query embedding
qemb = generate_query_embedding('database security patterns')
assert qemb is not None
assert len(qemb) == 384
print(f'Query embedding: {len(qemb)} dims')

# Test semantic similarity
similarity = np.dot(emb, qemb)
print(f'Similarity (RLS vs database security): {similarity:.3f}')
assert similarity > 0.2, 'Expected some semantic similarity'

# Test unrelated query
qemb2 = generate_query_embedding('chocolate cake recipe')
similarity2 = np.dot(emb, qemb2)
print(f'Similarity (RLS vs chocolate cake): {similarity2:.3f}')
assert similarity2 < similarity, 'Unrelated query should be less similar'

print('All embedding tests passed!')
"
```

### Level 4: Integration Tests
```bash
# After running migration and backfill:
.venv/Scripts/python.exe -c "
from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client
from agent.embedding import generate_query_embedding

client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY'))
team_id = os.getenv('PLAYBOOK_TEAM_ID')

# Check how many lessons have embeddings
result = client.table('lessons_learned').select('id, title, embedding').eq('team_id', team_id).execute()
with_emb = sum(1 for r in result.data if r.get('embedding'))
print(f'Lessons with embeddings: {with_emb}/{len(result.data)}')

# Test semantic search via RPC
query_emb = generate_query_embedding('database security and access control')
result = client.rpc('match_lessons', {
    'query_embedding': query_emb,
    'match_team_id': team_id,
    'match_threshold': 0.3,
    'match_count': 5
}).execute()
print(f'Semantic search results: {len(result.data)}')
for r in result.data:
    print(f'  [{r[\"similarity\"]:.3f}] {r[\"title\"]}')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from mcp_server.playbook_mcp import mcp; print('MCP import OK')"
```

## Final Validation Checklist
- [ ] pgvector extension enabled in Supabase
- [ ] `embedding vector(384)` column exists on `lessons_learned`
- [ ] `match_lessons` RPC function works
- [ ] `agent/embedding.py` generates correct 384-dim normalized vectors
- [ ] Backfill script updates all existing lessons
- [ ] Auto-capture generates embeddings on insert
- [ ] `playbook_share_lesson` generates embeddings on insert
- [ ] Graceful fallback when model unavailable (no crash)
- [ ] MCP server imports still work

## Anti-Patterns
- Do NOT store embeddings in local `data/lessons.json` — too large, only in Supabase
- Do NOT call `SentenceTransformer()` on every request — use singleton pattern
- Do NOT block lesson creation if embedding fails — embedding is enhancement, not requirement
- Do NOT use a different model dimension than 384 without updating the SQL column type
- Do NOT skip the IVFFlat index — without it, similarity search scans the full table
- Do NOT embed only the title — concatenate title + description + recommendation for richer semantics
