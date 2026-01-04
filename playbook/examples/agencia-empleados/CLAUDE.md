# JobMatch AI - Employment Agency SaaS

**AI-powered platform for employment agencies to match candidates with jobs**

---

## Core Principles

- **VERBOSE_NAMING** - Descriptive function names
- **TYPE_SAFETY** - All Python functions typed
- **AI_FRIENDLY_LOGGING** - Structured JSON logs
- **MULTI_TENANCY_FIRST** - agency_id on all tables

---

## Tech Stack

- **Backend:** FastAPI + Pydantic AI
- **Database:** Postgres + pgvector (for semantic matching)
- **Vector DB:** Pinecone (candidate/job embeddings)
- **Auth:** Supabase Auth
- **Frontend:** Next.js 14 + TypeScript
- **UI:** Tailwind + shadcn/ui
- **AI:** OpenAI GPT-4o-mini + embeddings

---

## Architecture

### Vertical Slice Architecture
```
features/
├── candidates/
│   ├── api.py          # FastAPI routes
│   ├── service.py      # Business logic
│   ├── repository.py   # DB access
│   └── models.py       # Pydantic models
├── jobs/
├── matching/           # AI matching engine
└── applications/
```

### AI Matching Pipeline
```
1. Job Posted → Generate embedding
2. Candidate Uploaded Resume → Parse + embed
3. Matching Engine → Semantic search (Pinecone)
4. Ranking → Pydantic AI agent scores matches
5. Notification → Top 5 candidates notified
```

---

## Code Style

**Pydantic Models:**
```python
from pydantic import BaseModel, Field
from typing import Optional

class Candidate(BaseModel):
    id: str
    agency_id: str
    name: str
    email: str
    phone: Optional[str] = None
    resume_text: str
    skills: list[str]
    years_experience: int = Field(ge=0)
    desired_salary: Optional[int] = None
```

**AI Agent Pattern:**
```python
from pydantic_ai import Agent

matching_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt="""You are an expert recruiter.
    Score how well a candidate matches a job posting.
    Consider: skills match, experience level, salary expectations.
    Output: Score 0-100 with explanation."""
)

async def score_match(candidate: Candidate, job: Job) -> MatchScore:
    result = await matching_agent.run(
        f"Candidate: {candidate.model_dump_json()}\nJob: {job.model_dump_json()}"
    )
    return MatchScore.model_validate_json(result.data)
```

---

## Database Schema

```sql
CREATE TABLE agencies (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT DEFAULT 'basic'
);

CREATE TABLE candidates (
    id UUID PRIMARY KEY,
    agency_id UUID REFERENCES agencies(id),
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    resume_url TEXT,
    resume_text TEXT,  -- Parsed resume
    embedding vector(1536),  -- OpenAI embedding
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    agency_id UUID REFERENCES agencies(id),
    company_name TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    salary_range TEXT,
    embedding vector(1536),
    status TEXT DEFAULT 'open',  -- open, filled, closed
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE matches (
    id UUID PRIMARY KEY,
    agency_id UUID REFERENCES agencies(id),
    candidate_id UUID REFERENCES candidates(id),
    job_id UUID REFERENCES jobs(id),
    score INTEGER,  -- 0-100
    explanation TEXT,
    status TEXT DEFAULT 'pending',  -- pending, accepted, rejected
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Vector similarity search (pgvector)
CREATE INDEX ON candidates USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON jobs USING ivfflat (embedding vector_cosine_ops);
```

---

## Common Patterns

### Pattern 1: Resume Parsing
```python
from langchain.document_loaders import PyPDFLoader

async def parse_resume(file_path: str) -> dict:
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    text = "\n".join([page.page_content for page in pages])

    # Extract with AI
    result = await extraction_agent.run(
        f"Extract name, email, skills, experience from:\n{text}"
    )

    return result.data
```

### Pattern 2: Semantic Job Matching
```python
async def find_matching_candidates(job: Job, top_k: int = 10):
    # Generate job embedding
    job_embedding = get_embedding(f"{job.title}\n{job.description}")

    # Semantic search in Pinecone
    results = pinecone_index.query(
        vector=job_embedding,
        top_k=top_k,
        filter={"agency_id": job.agency_id},
        include_metadata=True
    )

    # Score each match with AI
    scored_matches = []
    for match in results.matches:
        candidate = get_candidate(match.id)
        score = await matching_agent.run(candidate, job)
        scored_matches.append((candidate, score))

    return sorted(scored_matches, key=lambda x: x[1], reverse=True)
```

---

## Environment Variables

```bash
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX=job-matching
SENDGRID_API_KEY=...  # For notifications
```

---

**Multi-tenant SaaS para agencias de empleo con AI matching.**
