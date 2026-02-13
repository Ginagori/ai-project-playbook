"""
Playbook RAG Tool

Provides hybrid search over the AI Project Playbook content.
Combines keyword matching (30%) with category-based relevance scoring (70%)
for intelligent routing without requiring embeddings.

Inspired by OpenClaw's hybrid search pattern (vector-first + keyword fallback),
adapted to work without external embedding APIs.
"""

import json
import re
from pathlib import Path
from dataclasses import dataclass


PLAYBOOK_DIR = Path(__file__).parent.parent.parent / "playbook"
INDEX_FILE = Path(__file__).parent.parent.parent / ".playbook_index.json"


@dataclass
class SearchResult:
    """A search result from the playbook."""
    file: str
    title: str
    snippet: str
    score: float = 0.0


# =============================================================================
# Query Categories — maps user intent to playbook sections
# =============================================================================

QUERY_CATEGORIES = {
    "discovery": {
        "keywords": ["discovery", "question", "understand", "scope", "requirements", "objective", "kickoff", "start"],
        "priority_dirs": ["01-discovery"],
        "boost": 1.5,
    },
    "planning": {
        "keywords": ["plan", "claude.md", "prd", "global rules", "reference guide", "brainstorm", "vibe"],
        "priority_dirs": ["02-planning", "templates"],
        "boost": 1.5,
    },
    "roadmap": {
        "keywords": ["roadmap", "slash command", "feature breakdown", "sprint", "milestone", "prioritiz"],
        "priority_dirs": ["03-roadmap"],
        "boost": 1.5,
    },
    "implementation": {
        "keywords": ["implement", "piv loop", "validation pyramid", "code", "execute", "build", "pattern", "architecture", "vertical slice"],
        "priority_dirs": ["04-implementation"],
        "boost": 1.5,
    },
    "deployment": {
        "keywords": ["deploy", "docker", "kubernetes", "k8s", "netlify", "railway", "cloud run", "ci/cd", "github actions", "multi-tenancy"],
        "priority_dirs": ["05-deployment"],
        "boost": 1.5,
    },
    "advanced": {
        "keywords": ["advanced", "subagent", "parallel", "worktree", "context engineering", "meta-reasoning", "lovable", "archon"],
        "priority_dirs": ["06-advanced"],
        "boost": 1.3,
    },
    # New categories for NOVA/OpenClaw content
    "evals": {
        "keywords": ["eval", "test", "golden dataset", "pydantic-evals", "llm judge", "quality", "scoring", "rubric", "annotation", "feedback"],
        "priority_dirs": ["06-advanced"],
        "priority_files": ["agent-testing-evals.md"],
        "boost": 1.6,
    },
    "observability": {
        "keywords": ["observability", "langfuse", "trace", "span", "monitoring", "metrics", "latency", "opentelemetry", "otel", "dashboard"],
        "priority_dirs": ["06-advanced"],
        "priority_files": ["agent-observability.md"],
        "boost": 1.6,
    },
    "monetization": {
        "keywords": ["stripe", "billing", "token", "payment", "subscription", "pricing", "saas", "monetiz", "revenue", "webhook", "checkout"],
        "priority_dirs": ["06-advanced"],
        "priority_files": ["saas-monetization.md"],
        "boost": 1.6,
    },
    "memory": {
        "keywords": ["memory", "soul", "heartbeat", "cron", "proactive", "personality", "context window", "vector", "embedding", "rag", "hybrid search", "auto-capture"],
        "priority_dirs": ["06-advanced"],
        "priority_files": ["agent-memory-architecture.md"],
        "boost": 1.6,
    },
    "marketplace": {
        "keywords": ["marketplace", "plugin", "extension", "sdk", "multi-channel", "whatsapp", "telegram", "slack", "discord", "channel", "digital employee"],
        "priority_dirs": ["06-advanced"],
        "priority_files": ["marketplace-agent-development.md"],
        "boost": 1.6,
    },
    "security": {
        "keywords": ["security", "sandbox", "fail-closed", "allowlist", "approval", "permission", "auth", "rls", "row level", "env", "secret", "credential"],
        "priority_dirs": ["02-planning", "06-advanced"],
        "priority_files": ["security-best-practices.md", "agent-security-execution.md"],
        "boost": 1.5,
    },
    "system_review": {
        "keywords": ["system review", "meta-analysis", "confidence", "plan fidelity", "artifact quality", "retrospective"],
        "priority_dirs": ["04-implementation"],
        "priority_files": ["system-review-guide.md"],
        "boost": 1.5,
    },
}


def load_index() -> dict | None:
    """Load the playbook index if it exists."""
    if INDEX_FILE.exists():
        try:
            return json.loads(INDEX_FILE.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def extract_title(content: str) -> str:
    """Extract the first heading as title."""
    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def _classify_query(query: str) -> list[tuple[str, float]]:
    """
    Classify a query into one or more categories with confidence scores.

    Returns list of (category_name, confidence) sorted by confidence descending.
    """
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))
    scores = []

    for cat_name, cat_info in QUERY_CATEGORIES.items():
        cat_score = 0.0
        for keyword in cat_info["keywords"]:
            kw_lower = keyword.lower()
            # Exact phrase match (higher score)
            if kw_lower in query_lower:
                cat_score += 2.0
            # Word-level match
            elif any(kw_lower in w or w in kw_lower for w in query_words):
                cat_score += 1.0

        if cat_score > 0:
            scores.append((cat_name, cat_score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def _get_section_weight(file_path: str, categories: list[tuple[str, float]]) -> float:
    """
    Calculate section relevance weight based on detected categories.

    Returns a multiplier (1.0 = neutral, >1.0 = boosted, <1.0 = demoted).
    """
    if not categories:
        return 1.0

    file_str = file_path.replace("\\", "/").lower()
    max_boost = 1.0

    for cat_name, cat_confidence in categories[:3]:  # Top 3 categories
        cat_info = QUERY_CATEGORIES[cat_name]

        # Check priority directories
        for pdir in cat_info.get("priority_dirs", []):
            if pdir.lower() in file_str:
                max_boost = max(max_boost, cat_info["boost"])

        # Check priority files (exact match scores higher)
        for pfile in cat_info.get("priority_files", []):
            if pfile.lower() in file_str:
                max_boost = max(max_boost, cat_info["boost"] * 1.2)

    return max_boost


def search_hybrid(query: str, max_results: int = 5) -> list[SearchResult]:
    """
    Hybrid search combining keyword matching with category-based relevance.

    Scoring formula:
    - keyword_score * 0.3 + category_relevance * 0.7

    This approximates semantic search without requiring embeddings,
    using category detection and section-matching as a proxy.
    """
    results = []
    query_lower = query.lower()
    query_words = set(re.findall(r'\w+', query_lower))

    # Classify the query
    categories = _classify_query(query)

    for md_file in PLAYBOOK_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            content_lower = content.lower()
            rel_path = str(md_file.relative_to(PLAYBOOK_DIR))

            # --- Keyword score (0.3 weight) ---
            keyword_score = 0.0
            for word in query_words:
                if len(word) < 3:
                    continue
                count = content_lower.count(word)
                if count > 0:
                    # Normalize: diminishing returns for high counts
                    keyword_score += min(count, 20) / 20.0

            if len(query_words) > 0:
                keyword_score = keyword_score / len(query_words)

            # Bonus for title match
            title = extract_title(content)
            title_lower = title.lower()
            if any(w in title_lower for w in query_words if len(w) > 3):
                keyword_score *= 1.5

            # Bonus for exact phrase match
            if query_lower in content_lower:
                keyword_score *= 2.0

            # --- Category relevance score (0.7 weight) ---
            section_weight = _get_section_weight(rel_path, categories)
            category_score = (section_weight - 1.0) / 1.0  # Normalize: 0.0 for neutral, ~0.5-1.0 for boosted

            # --- Combined score ---
            combined = (keyword_score * 0.3) + (category_score * 0.7)

            if combined > 0.01 or keyword_score > 0.1:
                # Get snippet around best match
                snippet = _extract_snippet(content, content_lower, query_words, query_lower)

                results.append(SearchResult(
                    file=rel_path,
                    title=title,
                    snippet=snippet,
                    score=combined,
                ))
        except Exception:
            continue

    results.sort(key=lambda x: x.score, reverse=True)
    return results[:max_results]


def _extract_snippet(content: str, content_lower: str, query_words: set, query_lower: str) -> str:
    """Extract the most relevant snippet from content."""
    # Try exact phrase match first
    pos = content_lower.find(query_lower)
    if pos == -1:
        # Fall back to first keyword match
        for word in query_words:
            if len(word) < 3:
                continue
            pos = content_lower.find(word)
            if pos >= 0:
                break

    if pos < 0:
        pos = 0

    start = max(0, pos - 100)
    end = min(len(content), pos + 400)
    snippet = content[start:end].replace("\n", " ").strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."

    return snippet


def search_keyword(query: str, max_results: int = 5) -> list[SearchResult]:
    """
    Simple keyword search in playbook files.
    Kept for backward compatibility — internally uses hybrid search.
    """
    return search_hybrid(query, max_results)


def search_by_phase(phase: str) -> list[SearchResult]:
    """
    Search for content related to a specific phase.

    Args:
        phase: Phase name (discovery, planning, roadmap, implementation, deployment)

    Returns:
        List of SearchResult objects
    """
    phase_dirs = {
        "discovery": "01-discovery",
        "planning": "02-planning",
        "roadmap": "03-roadmap",
        "implementation": "04-implementation",
        "deployment": "05-deployment",
        "advanced": "06-advanced",
    }

    dir_name = phase_dirs.get(phase.lower())
    if not dir_name:
        return search_hybrid(phase)

    phase_dir = PLAYBOOK_DIR / dir_name
    if not phase_dir.exists():
        return []

    results = []
    for md_file in phase_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            results.append(SearchResult(
                file=str(md_file.relative_to(PLAYBOOK_DIR)),
                title=extract_title(content),
                snippet=content[:500].replace("\n", " ").strip() + "...",
                score=1.0,
            ))
        except Exception:
            continue

    return results


def search_by_topic(topic: str) -> list[SearchResult]:
    """
    Search for content related to a specific topic.

    Uses hybrid search for intelligent routing.
    Falls back to topic_map for known topics.

    Args:
        topic: Topic name

    Returns:
        List of SearchResult objects
    """
    topic_map = {
        "claude.md": ["02-planning/claude-md-creation.md"],
        "prd": ["templates/prd-template.md", "02-planning/reference-guides.md"],
        "piv loop": ["04-implementation/piv-loop-execution.md", "04-implementation/piv-loop-workflow.md"],
        "validation": ["04-implementation/validation-pyramid.md"],
        "testing": ["04-implementation/validation-pyramid.md", "templates/validate-command.md"],
        "deployment": ["05-deployment/deployment-phases.md", "05-deployment/mvp-deployment.md"],
        "docker": ["05-deployment/docker/Dockerfile", "templates/docker-compose.yml"],
        "kubernetes": ["05-deployment/kubernetes/deployment.yaml", "05-deployment/scale-deployment.md"],
        "multi-tenancy": ["05-deployment/multi-tenancy-design.md"],
        "lovable": ["06-advanced/lovable-to-production.md"],
        "agents": ["06-advanced/subagents-framework.md", "06-advanced/parallel-implementation.md"],
        "security": ["02-planning/security-best-practices.md", "06-advanced/agent-security-execution.md"],
        "architecture": ["04-implementation/architecture-patterns-guide.md", "04-implementation/vertical-slice-guide.md"],
        # New topics for NOVA/OpenClaw content
        "evals": ["06-advanced/agent-testing-evals.md"],
        "observability": ["06-advanced/agent-observability.md"],
        "langfuse": ["06-advanced/agent-observability.md"],
        "stripe": ["06-advanced/saas-monetization.md"],
        "billing": ["06-advanced/saas-monetization.md"],
        "monetization": ["06-advanced/saas-monetization.md"],
        "memory": ["06-advanced/agent-memory-architecture.md"],
        "heartbeat": ["06-advanced/agent-memory-architecture.md"],
        "marketplace": ["06-advanced/marketplace-agent-development.md"],
        "plugin": ["06-advanced/marketplace-agent-development.md"],
        "multi-channel": ["06-advanced/marketplace-agent-development.md"],
        "sandbox": ["06-advanced/agent-security-execution.md"],
        "system review": ["04-implementation/system-review-guide.md"],
        "prp": ["templates/prp-template.md"],
    }

    # Find matching topic
    topic_lower = topic.lower()
    matching_files = []
    for key, files in topic_map.items():
        if key in topic_lower or topic_lower in key:
            matching_files.extend(files)

    if not matching_files:
        # Fall back to hybrid search
        return search_hybrid(topic)

    results = []
    for file_path in matching_files:
        full_path = PLAYBOOK_DIR / file_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding="utf-8")
                results.append(SearchResult(
                    file=file_path,
                    title=extract_title(content),
                    snippet=content[:500].replace("\n", " ").strip() + "...",
                    score=1.0,
                ))
            except Exception:
                continue

    # If topic_map returned results, also search for more via hybrid
    if len(results) < 3:
        hybrid_results = search_hybrid(topic, max_results=3)
        existing_files = {r.file for r in results}
        for hr in hybrid_results:
            if hr.file not in existing_files:
                results.append(hr)

    return results


def get_file_content(file_path: str) -> str | None:
    """
    Get the full content of a playbook file.

    Args:
        file_path: Relative path within the playbook directory

    Returns:
        File content or None if not found
    """
    full_path = PLAYBOOK_DIR / file_path
    if full_path.exists():
        try:
            return full_path.read_text(encoding="utf-8")
        except Exception:
            return None
    return None


def format_search_results(results: list[SearchResult]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    output = f"## Found {len(results)} results\n\n"
    for i, result in enumerate(results, 1):
        score_bar = "=" * int(result.score * 10) if result.score <= 1.0 else "=" * 10
        output += f"### {i}. {result.title}\n"
        output += f"**File**: `{result.file}` | **Relevance**: [{score_bar}] {result.score:.2f}\n"
        output += f"```\n{result.snippet}\n```\n\n"

    return output


# =============================================================================
# Main search function used by the agent
# =============================================================================

def search_playbook(query: str, search_type: str = "keyword", max_results: int = 5) -> str:
    """
    Search the playbook with the given query.

    Args:
        query: Search query
        search_type: Type of search - "keyword", "phase", or "topic"
        max_results: Maximum number of results

    Returns:
        Formatted search results
    """
    if search_type == "phase":
        results = search_by_phase(query)
    elif search_type == "topic":
        results = search_by_topic(query)
    else:
        results = search_hybrid(query, max_results)

    return format_search_results(results)
