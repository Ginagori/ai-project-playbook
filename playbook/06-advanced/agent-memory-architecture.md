# Agent Memory Architecture Guide

A comprehensive guide for building memory systems for AI agents — the 4+1 file system, vector-first search, heartbeat patterns, context window guard, and personality evolution.

## Why Memory Matters

Without memory, every conversation starts from zero. The agent doesn't know:
- Who the user is or what they prefer
- What decisions were made in previous sessions
- What tasks are pending or completed
- What patterns to follow based on experience

Memory transforms a stateless LLM into a persistent, evolving agent.

---

## The 4+1 File System

Inspired by OpenClaw and NOVA's Paddy agent, this architecture separates memory into distinct concerns:

```
agents/{agent_id}/
├── soul.md        # Static personality and values (creator-defined)
├── user.md        # Per-user preferences and history (dynamic)
├── memory.md      # Shared factual knowledge (dynamic)
├── sessions/      # Conversation logs (append-only)
│   ├── 2025-01-01_abc123.json
│   └── 2025-01-02_def456.json
└── heartbeat.md   # Scheduled tasks and proactive behaviors (+1)
```

### soul.md — Agent Personality (Static)

Defines who the agent IS. Set by the creator, rarely changes.

```markdown
# Soul — Project Manager Agent

## Identity
I am an AI Project Manager that guides development teams from idea to deployment.

## Values
- Clarity over cleverness
- Ship early, iterate fast
- Security is non-negotiable
- Test everything, assume nothing

## Communication Style
- Professional but approachable
- Use concrete examples over abstract explanations
- Ask clarifying questions rather than assuming
- Celebrate progress, be honest about problems

## Boundaries
- I do not write production code directly
- I always recommend testing before deploying
- I escalate security decisions to humans
- I do not make financial decisions autonomously
```

### user.md — User Preferences (Dynamic)

Per-user profile that grows over time.

```markdown
# User Profile — natalia

## Preferences
- Prefers Spanish for casual conversation, English for technical docs
- Likes concise responses, not verbose
- Values security-first approach
- Uses VSCode with Antigravity extension

## Tech Stack Preferences
- Python + FastAPI for backends
- Next.js + TypeScript for frontends
- Supabase for database
- Tailwind CSS for styling

## Working Style
- Prefers to review plans before execution
- Likes numbered lists for action items
- Wants cost estimates for cloud services
- Works mostly evenings and weekends

## History
- Completed: AI Project Playbook Agent (10 sessions)
- Current: Upgrading Playbook with NOVA patterns
- Goal: Build NOVA AI Operations Center
```

### memory.md — Shared Knowledge (Dynamic)

Factual knowledge extracted from conversations.

```markdown
# Agent Memory

## Decisions
- 2025-01-03: Architecture chosen — LangGraph for orchestration
- 2025-01-05: Database — Supabase with pgvector for RAG
- 2025-01-05: Team: Nivanta AI, 2-3 developers

## Entities
- NOVA: AI Operations Center ($49-499+/mo)
- Paddy: Super-agent orchestrator for NOVA
- Playbook Agent: PM agent, digital employee in NOVA marketplace

## Facts
- Supabase project ID: lnuyanxodyuoadawvjle
- Team ID: 9f1c0ad9-3ba3-4ccf-8a02-fcbb94fcab6d
- MCP Server has 33 tools
- Playbook has ~71 files, ~39K lines
```

### heartbeat.md — Scheduled Tasks (+1)

Proactive behaviors the agent performs without being asked.

```markdown
# Heartbeat Schedule

## Daily
- 09:00 UTC: Check for stale projects (no activity > 7 days)
- 18:00 UTC: Generate daily summary of team activity

## Weekly
- Monday 10:00: Review open projects, suggest priorities
- Friday 17:00: Weekly progress report

## On Events
- On project_completed: Auto-capture lessons learned
- On phase_transition: Auto-evaluate artifact quality
- On error_detected: Suggest system improvement
```

---

## Memory Implementation

### Core Memory Class

```python
from pathlib import Path
from datetime import datetime

class AgentMemory:
    def __init__(self, agent_id: str, base_dir: str = "agents"):
        self.agent_id = agent_id
        self.base = Path(base_dir) / agent_id
        self.base.mkdir(parents=True, exist_ok=True)

        self.soul = self._load("soul.md")
        self.memory = self._load("memory.md")
        self.heartbeat = self._load("heartbeat.md")
        self.user_profiles: dict[str, str] = {}

    def _load(self, filename: str) -> str:
        path = self.base / filename
        return path.read_text() if path.exists() else ""

    def _save(self, filename: str, content: str):
        (self.base / filename).write_text(content)

    def get_user_profile(self, user_id: str) -> str:
        if user_id not in self.user_profiles:
            path = self.base / "users" / f"{user_id}.md"
            self.user_profiles[user_id] = path.read_text() if path.exists() else ""
        return self.user_profiles[user_id]

    def get_system_prompt(self, user_id: str) -> str:
        """Build system prompt with all memory injected."""
        user_profile = self.get_user_profile(user_id)

        return f"""{self.soul}

## About This User
{user_profile if user_profile else "New user — no history yet."}

## Things I Remember
{self.memory}

## Current Date
{datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
"""

    def update_user_profile(self, user_id: str, content: str):
        """Update a user's profile."""
        path = self.base / "users"
        path.mkdir(exist_ok=True)
        (path / f"{user_id}.md").write_text(content)
        self.user_profiles[user_id] = content

    def add_memory(self, category: str, content: str):
        """Add a new memory entry."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d")
        entry = f"- {timestamp}: {content}"
        self.memory += f"\n{entry}" if self.memory else entry
        self._save("memory.md", self.memory)
```

---

## Memory Curation

### What to Store vs Discard

| Store (Permanent) | Discard (Ephemeral) |
|-------------------|---------------------|
| User preferences | Greeting messages |
| Architectural decisions | Small talk |
| Tech stack choices | Repeated questions |
| Project milestones | Intermediate reasoning |
| Contact information | Draft iterations |
| Error patterns | One-time instructions |

### Memory Categories

```python
from enum import Enum

class MemoryCategory(Enum):
    PREFERENCE = "preference"   # "I prefer dark mode"
    DECISION = "decision"       # "We decided on PostgreSQL"
    ENTITY = "entity"           # "My company is Nivanta AI"
    FACT = "fact"               # "The API rate limit is 100/min"
    INSTRUCTION = "instruction" # "Always use TypeScript strict mode"
```

### Importance Scoring

```python
def score_importance(content: str, category: MemoryCategory) -> int:
    """Score memory importance from 1-10."""
    base_scores = {
        MemoryCategory.PREFERENCE: 6,
        MemoryCategory.DECISION: 8,
        MemoryCategory.ENTITY: 5,
        MemoryCategory.FACT: 4,
        MemoryCategory.INSTRUCTION: 9,
    }
    score = base_scores.get(category, 5)

    # Boost for emphatic language
    if any(word in content.lower() for word in ["always", "never", "critical", "important"]):
        score = min(10, score + 2)

    # Boost for technical specifics
    if any(char in content for char in ["=", ".", "/", ":"]):
        score = min(10, score + 1)

    return score
```

---

## Auto-Capture Triggers

Inspired by OpenClaw — the agent automatically detects memorable content without the user explicitly asking.

```python
import re

MEMORY_TRIGGERS = [
    # Explicit requests
    (r"(?:remember|don't forget|keep in mind)\s+(.+)", MemoryCategory.INSTRUCTION),
    # Preferences
    (r"(?:I prefer|I always|I never|I like|I hate)\s+(.+)", MemoryCategory.PREFERENCE),
    # Decisions
    (r"(?:we decided|let's go with|the plan is|we'll use)\s+(.+)", MemoryCategory.DECISION),
    # Identity/entities
    (r"(?:my name is|I work at|I'm from|our company is)\s+(.+)", MemoryCategory.ENTITY),
    # Technical facts
    (r"(?:the (?:API|URL|key|endpoint|port) is)\s+(.+)", MemoryCategory.FACT),
]

def detect_memorable_content(message: str) -> list[dict]:
    """Scan message for auto-capture triggers."""
    candidates = []
    for pattern, category in MEMORY_TRIGGERS:
        matches = re.findall(pattern, message, re.IGNORECASE)
        for match in matches:
            candidates.append({
                "content": match.strip(),
                "category": category,
                "importance": score_importance(match, category),
                "source": "auto-capture",
                "trigger": pattern,
            })
    return candidates

# Integration in agent loop
async def process_message(message: str, memory: AgentMemory, user_id: str):
    # Detect memorable content
    candidates = detect_memorable_content(message)
    for candidate in candidates:
        if candidate["importance"] >= 5:  # Only store important memories
            memory.add_memory(
                category=candidate["category"].value,
                content=candidate["content"],
            )

    # Generate response with memory context
    system_prompt = memory.get_system_prompt(user_id)
    response = await llm.generate(system_prompt, message)

    # Also check response for auto-capture (agent's own decisions)
    agent_candidates = detect_memorable_content(response)
    for candidate in agent_candidates:
        if candidate["importance"] >= 7:
            memory.add_memory(
                category=candidate["category"].value,
                content=f"(agent) {candidate['content']}",
            )

    return response
```

---

## Vector-First Memory

For large memory stores, keyword search isn't enough. Vector search finds semantically similar memories even when exact words don't match.

### Hybrid Search: 70% Vector + 30% Keyword

```python
class VectorMemory:
    """Vector-first memory with hybrid search."""

    def __init__(self, embedding_model, db):
        self.embedder = embedding_model
        self.db = db  # pgvector, LanceDB, or Pinecone

    async def store(self, content: str, metadata: dict):
        """Store a memory with its embedding."""
        embedding = await self.embedder.embed(content)
        await self.db.insert({
            "content": content,
            "embedding": embedding,
            "category": metadata.get("category", "general"),
            "importance": metadata.get("importance", 5),
            "user_id": metadata.get("user_id"),
            "created_at": datetime.utcnow().isoformat(),
        })

    async def search(self, query: str, limit: int = 10,
                     user_id: str | None = None) -> list[dict]:
        """Hybrid search: 70% vector similarity + 30% keyword match."""
        query_embedding = await self.embedder.embed(query)

        # Vector search
        vector_results = await self.db.vector_search(
            query_embedding, limit=limit * 2,
            filter={"user_id": user_id} if user_id else None,
        )

        # Keyword search
        keyword_results = await self.db.keyword_search(
            query, limit=limit * 2,
            filter={"user_id": user_id} if user_id else None,
        )

        # Combine with weights
        combined = {}
        for r in vector_results:
            combined[r["id"]] = {
                "score": r["similarity"] * 0.7,
                "memory": r,
            }
        for r in keyword_results:
            key = r["id"]
            if key in combined:
                combined[key]["score"] += r["rank_score"] * 0.3
            else:
                combined[key] = {
                    "score": r["rank_score"] * 0.3,
                    "memory": r,
                }

        # Sort by combined score and return top results
        ranked = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
        return [item["memory"] for item in ranked[:limit]]
```

### Storage Options

| Storage | Type | Best For | Cost |
|---------|------|----------|------|
| **LanceDB** | Local file | Development, single-user | Free |
| **pgvector** (Supabase) | Managed PostgreSQL | Production, multi-tenant | $25+/mo |
| **Pinecone** | Cloud vector DB | Large-scale, serverless | $70+/mo |
| **Chroma** | Local/cloud | Prototyping | Free/paid |

### Supabase pgvector Setup

```sql
-- Enable vector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Memories table
CREATE TABLE agent_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    user_id TEXT,
    content TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'general',
    importance INTEGER DEFAULT 5 CHECK (importance BETWEEN 1 AND 10),
    embedding vector(1536),  -- OpenAI ada-002 dimension
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Vector similarity search index
CREATE INDEX idx_memories_embedding ON agent_memories
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Keyword search index
CREATE INDEX idx_memories_content ON agent_memories
    USING gin (to_tsvector('english', content));
```

---

## Session Management

### Session Lifecycle

```python
from dataclasses import dataclass, field

@dataclass
class SessionLog:
    session_id: str
    user_id: str
    agent_id: str
    started_at: datetime
    messages: list[dict] = field(default_factory=list)
    total_tokens: int = 0
    total_bytes: int = 0

    MAX_MESSAGES = 50
    MAX_BYTES = 100 * 1024  # 100KB

    def add_message(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self.total_bytes += len(content.encode())
        self.total_tokens += len(content) // 4  # rough estimate

    def should_compact(self) -> bool:
        return (
            len(self.messages) >= self.MAX_MESSAGES
            or self.total_bytes >= self.MAX_BYTES
        )
```

### Session Compaction

```python
async def compact_session(session: SessionLog, llm) -> str:
    """Summarize old messages when session gets too long."""
    # Keep last 10 messages verbatim
    recent = session.messages[-10:]
    old = session.messages[:-10]

    if not old:
        return ""

    # Summarize old messages
    old_text = "\n".join(f"{m['role']}: {m['content']}" for m in old)
    summary = await llm.generate(
        system="Summarize this conversation history concisely. Keep key decisions, "
               "preferences, and action items. Omit greetings and small talk.",
        user=old_text,
    )

    # Replace old messages with summary
    session.messages = [
        {"role": "system", "content": f"[Previous conversation summary]\n{summary}"}
    ] + recent
    session.total_bytes = sum(len(m["content"].encode()) for m in session.messages)

    return summary
```

---

## Heartbeat Pattern

> For the full agent architecture context (Triple-Layer Soul, 4 Engines, Security Model), see [autonomous-agent-architecture.md](./autonomous-agent-architecture.md).

Inspired by OpenClaw — agents that act proactively without being asked.

### Schedule Types

```python
from dataclasses import dataclass
from typing import Literal

@dataclass
class HeartbeatSchedule:
    type: Literal["every", "at", "cron"]
    value: str  # "5min", "2025-01-01T09:00", "0 9 * * 1-5"
    action: str
    payload: dict = field(default_factory=dict)
    wake_mode: Literal["now", "next-heartbeat"] = "next-heartbeat"
    enabled: bool = True

# Examples
schedules = [
    # Every 30 minutes: check agent health
    HeartbeatSchedule(
        type="every", value="30min",
        action="check_agent_health",
        payload={"agents": ["researcher", "coder", "reviewer"]},
    ),

    # Weekday mornings: daily briefing
    HeartbeatSchedule(
        type="cron", value="0 9 * * 1-5",
        action="morning_briefing",
        payload={"include": ["stale_projects", "pending_reviews"]},
    ),

    # Specific date: quarterly review
    HeartbeatSchedule(
        type="at", value="2025-04-01T10:00",
        action="quarterly_review",
    ),
]
```

### Heartbeat Runner

```python
import asyncio
from croniter import croniter
from datetime import datetime, timedelta

class HeartbeatRunner:
    def __init__(self, agent, schedules: list[HeartbeatSchedule]):
        self.agent = agent
        self.schedules = schedules

    async def run(self):
        """Main heartbeat loop."""
        while True:
            now = datetime.utcnow()
            for schedule in self.schedules:
                if not schedule.enabled:
                    continue
                if self._should_fire(schedule, now):
                    asyncio.create_task(self._execute(schedule))
            await asyncio.sleep(60)  # Check every minute

    def _should_fire(self, schedule: HeartbeatSchedule, now: datetime) -> bool:
        if schedule.type == "every":
            # Parse interval (e.g., "30min", "1h", "24h")
            return self._check_interval(schedule, now)
        elif schedule.type == "cron":
            cron = croniter(schedule.value, now - timedelta(minutes=1))
            next_fire = cron.get_next(datetime)
            return abs((next_fire - now).total_seconds()) < 60
        elif schedule.type == "at":
            target = datetime.fromisoformat(schedule.value)
            return abs((target - now).total_seconds()) < 60
        return False

    async def _execute(self, schedule: HeartbeatSchedule):
        """Execute a heartbeat action."""
        try:
            await self.agent.handle_heartbeat(
                action=schedule.action,
                payload=schedule.payload,
            )
        except Exception as e:
            print(f"Heartbeat error: {schedule.action}: {e}")
```

### Proactive Use Cases

| Action | Trigger | Behavior |
|--------|---------|----------|
| Morning briefing | Weekdays 9am | Summarize stale projects, pending reviews |
| Health check | Every 30min | Verify agents are responding |
| Stale project alert | Daily | Flag projects with no activity >7 days |
| Token alert | On deduction | Warn when balance <20% |
| Weekly report | Friday 5pm | Progress summary for the week |

---

## Context Window Guard

Inspired by OpenClaw — proactively manage context window size to prevent overflow.

```python
class ContextWindowGuard:
    """Proactive context window management."""

    def __init__(self, max_tokens: int = 128000):
        self.max_tokens = max_tokens
        self.hard_minimum = 16000     # Reserved for response generation
        self.warning_threshold = 32000 # Start warning here

    def check(self, current_tokens: int) -> str:
        """Check context window state."""
        remaining = self.max_tokens - current_tokens

        if remaining < self.hard_minimum:
            return "shouldBlock"
        elif remaining < self.warning_threshold:
            return "shouldWarn"
        return "normal"

    def get_strategy(self, state: str) -> list[str]:
        """Get compression strategies for the current state."""
        if state == "shouldBlock":
            return [
                "summarize_all_messages",
                "drop_tool_outputs",
                "compress_memory",
                "keep_only_last_5_messages",
            ]
        elif state == "shouldWarn":
            return [
                "summarize_old_messages",
                "compact_tool_outputs",
                "trim_memory_to_recent",
            ]
        return []

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars ≈ 1 token)."""
        return len(text) // 4
```

### Integration

```python
async def agent_turn(messages: list[dict], memory: AgentMemory, guard: ContextWindowGuard):
    """Process an agent turn with context window protection."""
    # Estimate current context size
    total_text = "\n".join(m["content"] for m in messages)
    total_text += memory.get_system_prompt(user_id)
    current_tokens = guard.estimate_tokens(total_text)

    state = guard.check(current_tokens)

    if state == "shouldBlock":
        # Aggressive compression
        messages = await compress_messages(messages, keep_last=3)
        memory_text = memory.get_compressed_memory(max_tokens=2000)
    elif state == "shouldWarn":
        # Moderate compression
        messages = await compress_messages(messages, keep_last=10)

    # Now safe to call LLM
    response = await llm.generate(messages=messages)
    return response
```

---

## Unified RAG

Query across multiple memory sources with priority ordering.

```python
class UnifiedRAG:
    """Federated search across all memory sources."""

    def __init__(self, vector_memory, file_memory, session_store):
        self.vector = vector_memory
        self.files = file_memory
        self.sessions = session_store

    async def search(self, query: str, user_id: str, limit: int = 10) -> list[dict]:
        """Search all sources with priority ordering."""
        results = []

        # Priority 1: Recent memories (highest weight)
        recent = await self.vector.search(
            query, limit=limit, user_id=user_id,
        )
        for r in recent:
            r["source"] = "memory"
            r["priority"] = 3
        results.extend(recent)

        # Priority 2: Session history
        session_results = await self.sessions.search(
            query, user_id=user_id, limit=limit,
        )
        for r in session_results:
            r["source"] = "session"
            r["priority"] = 2
        results.extend(session_results)

        # Priority 3: Documentation
        doc_results = await self.files.search(query, limit=limit)
        for r in doc_results:
            r["source"] = "docs"
            r["priority"] = 1
        results.extend(doc_results)

        # Sort by priority then score, deduplicate
        results.sort(key=lambda x: (x["priority"], x.get("score", 0)), reverse=True)
        return self._deduplicate(results)[:limit]
```

---

## Meta-Skills

Agent creates reusable skills based on repeated patterns.

```python
class MetaSkillDetector:
    """Detect patterns that should become reusable skills."""

    def __init__(self, threshold: int = 3):
        self.pattern_counts: dict[str, int] = {}
        self.threshold = threshold

    def record_action(self, action_type: str, details: str):
        """Record an action and check if it should become a skill."""
        key = f"{action_type}:{self._normalize(details)}"
        self.pattern_counts[key] = self.pattern_counts.get(key, 0) + 1

        if self.pattern_counts[key] == self.threshold:
            return self._suggest_skill(action_type, details)
        return None

    def _suggest_skill(self, action_type: str, details: str) -> dict:
        return {
            "suggestion": f"Create a reusable skill for: {action_type}",
            "pattern": details,
            "frequency": self.threshold,
            "recommended_name": self._generate_skill_name(action_type),
        }
```

---

## Implementation Checklist

### Basic Memory
- [ ] soul.md defined for agent personality
- [ ] user.md storage per user
- [ ] memory.md for shared knowledge
- [ ] System prompt injection with memory context
- [ ] Session logging

### Auto-Capture
- [ ] Trigger patterns defined (remember, prefer, decided)
- [ ] Importance scoring implemented
- [ ] Auto-capture integrated in message loop
- [ ] Memory deduplication

### Vector Memory (if needed)
- [ ] Embedding model selected
- [ ] pgvector or LanceDB configured
- [ ] Hybrid search (70% vector + 30% keyword)
- [ ] Memory categories and importance filtering

### Heartbeat (if needed)
- [ ] Schedule types (every, at, cron)
- [ ] Heartbeat runner with async execution
- [ ] Morning briefing configured
- [ ] Health checks for sub-agents

### Context Window
- [ ] Guard configured with thresholds
- [ ] Compression strategies implemented
- [ ] Session compaction for long conversations
- [ ] Token estimation in message loop
