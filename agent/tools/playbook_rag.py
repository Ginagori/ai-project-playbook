"""
Playbook RAG Tool

Provides semantic search over the AI Project Playbook content.
Currently uses keyword-based search, will be upgraded to vector search with Supabase pgvector.
"""

import json
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


def search_keyword(query: str, max_results: int = 5) -> list[SearchResult]:
    """
    Simple keyword search in playbook files.

    Args:
        query: Search query
        max_results: Maximum number of results

    Returns:
        List of SearchResult objects
    """
    results = []
    query_lower = query.lower()
    query_words = set(query_lower.split())

    for md_file in PLAYBOOK_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            content_lower = content.lower()

            # Simple scoring based on word matches
            score = 0
            for word in query_words:
                if word in content_lower:
                    score += content_lower.count(word)

            if score > 0:
                # Get snippet around first match
                first_match_pos = content_lower.find(query_words.pop() if query_words else query_lower)
                start = max(0, first_match_pos - 100)
                end = min(len(content), first_match_pos + 400)
                snippet = content[start:end].replace("\n", " ").strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(content):
                    snippet = snippet + "..."

                results.append(SearchResult(
                    file=str(md_file.relative_to(PLAYBOOK_DIR)),
                    title=extract_title(content),
                    snippet=snippet,
                    score=score,
                ))
        except Exception:
            continue

    # Sort by score descending
    results.sort(key=lambda x: x.score, reverse=True)
    return results[:max_results]


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
        return search_keyword(phase)

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

    Maps common topics to relevant files.

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
        "security": ["02-planning/security-best-practices.md"],
        "architecture": ["04-implementation/architecture-patterns-guide.md", "04-implementation/vertical-slice-guide.md"],
    }

    # Find matching topic
    topic_lower = topic.lower()
    matching_files = []
    for key, files in topic_map.items():
        if key in topic_lower or topic_lower in key:
            matching_files.extend(files)

    if not matching_files:
        return search_keyword(topic)

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
        output += f"### {i}. {result.title}\n"
        output += f"**File**: `{result.file}`\n"
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
        results = search_keyword(query, max_results)

    return format_search_results(results)
