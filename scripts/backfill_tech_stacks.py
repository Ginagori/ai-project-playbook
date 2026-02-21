"""
Backfill tech_stacks in existing lessons.

Analyzes lesson title, description, recommendation, and tags to infer
which technologies each lesson applies to. Uses the same canonical
vocabulary as the orchestrator's discovery questions.

Usage:
    .venv/Scripts/python.exe scripts/backfill_tech_stacks.py [--dry-run] [--supabase]

Flags:
    --dry-run   Show what would change without writing
    --supabase  Also update Supabase lessons (requires env vars)
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Canonical tech_stack values (from orchestrator DISCOVERY_QUESTIONS):
#   Frontend: react-vite, nextjs, vue-nuxt, none
#   Backend:  fastapi, express, django, serverless
#   Database: postgresql-supabase, mongodb, sqlite, firebase

# Mapping: keyword found in tags/title/description/recommendation → canonical value
TECH_INFERENCE_MAP: dict[str, str] = {
    # Frontend — React ecosystem
    "react": "react-vite",
    "shadcn": "react-vite",
    "react-hook-form": "react-vite",
    "vite": "react-vite",
    # Frontend — Next.js (more specific, checked after react)
    "nextjs": "nextjs",
    "next.js": "nextjs",
    "middleware de next": "nextjs",
    # Frontend — Vue
    "vue": "vue-nuxt",
    "nuxt": "vue-nuxt",
    # Backend — FastAPI / Python
    "fastapi": "fastapi",
    "pydantic": "fastapi",
    "uvicorn": "fastapi",
    "uv": "fastapi",
    # Backend — Express / Node
    "express": "express",
    "nodejs": "express",
    # Backend — Django
    "django": "django",
    # Database — Supabase / PostgreSQL
    "supabase": "postgresql-supabase",
    "rls": "postgresql-supabase",
    "row-level-security": "postgresql-supabase",
    "postgresql": "postgresql-supabase",
    "postgres": "postgresql-supabase",
    # Database — MongoDB
    "mongodb": "mongodb",
    "mongo": "mongodb",
    # Database — Firebase
    "firebase": "firebase",
    # Database — SQLite
    "sqlite": "sqlite",
    # Extras that imply a stack
    "tailwind": "react-vite",  # In our context, always used with React
    "typescript": "react-vite",  # Most TS lessons are frontend React
}

# Keywords that override "react-vite" → "nextjs" when both match
# (Next.js IS React, but the canonical value should be "nextjs")
NEXTJS_INDICATORS = {"nextjs", "next.js", "middleware de next", "monorepo con next"}


def infer_tech_stacks(lesson: dict) -> list[str]:
    """Analyze lesson fields to infer tech_stacks.

    Returns a sorted list of canonical tech_stack values.
    """
    searchable = " ".join([
        lesson.get("title", ""),
        lesson.get("description", ""),
        lesson.get("recommendation", ""),
        " ".join(lesson.get("tags", [])),
    ]).lower()

    inferred: set[str] = set()
    has_nextjs_indicator = False

    for keyword, tech in TECH_INFERENCE_MAP.items():
        if keyword in searchable:
            inferred.add(tech)
            if keyword in NEXTJS_INDICATORS:
                has_nextjs_indicator = True

    # If both react-vite and nextjs matched, and there's a nextjs indicator,
    # remove react-vite (nextjs is more specific)
    if has_nextjs_indicator and "react-vite" in inferred and "nextjs" in inferred:
        inferred.discard("react-vite")

    return sorted(inferred)


def backfill_local(dry_run: bool = False) -> dict[str, int]:
    """Backfill tech_stacks in data/lessons.json.

    Returns stats dict with counts.
    """
    lessons_file = Path(__file__).parent.parent / "data" / "lessons.json"
    data = json.loads(lessons_file.read_text(encoding="utf-8"))
    lessons = data.get("lessons", [])

    updated = 0
    already_populated = 0
    no_match = 0

    for lesson in lessons:
        if lesson.get("tech_stacks"):
            already_populated += 1
            continue

        inferred = infer_tech_stacks(lesson)
        if inferred:
            if dry_run:
                print(f"  WOULD UPDATE: [{lesson.get('category')}] {lesson.get('title')}")
                print(f"    -> tech_stacks: {inferred}")
            else:
                lesson["tech_stacks"] = inferred
            updated += 1
        else:
            no_match += 1
            if dry_run:
                print(f"  NO MATCH: [{lesson.get('category')}] {lesson.get('title')}")
                print(f"    tags: {lesson.get('tags', [])}")

    if not dry_run:
        lessons_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    stats = {
        "total": len(lessons),
        "updated": updated,
        "already_populated": already_populated,
        "no_match": no_match,
    }

    return stats


def backfill_supabase(dry_run: bool = False) -> dict[str, int]:
    """Backfill tech_stacks in Supabase lessons_learned table.

    Returns stats dict with counts.
    """
    from dotenv import load_dotenv
    from supabase import create_client

    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    team_id = os.getenv("PLAYBOOK_TEAM_ID")

    if not all([supabase_url, supabase_key, team_id]):
        print("Error: Missing Supabase env vars")
        return {"total": 0, "updated": 0, "already_populated": 0, "no_match": 0}

    client = create_client(supabase_url, supabase_key)

    # Fetch all team lessons
    result = (
        client.table("lessons_learned")
        .select("id, title, description, recommendation, tags, tech_stacks, category")
        .eq("team_id", team_id)
        .execute()
    )

    lessons = result.data or []
    updated = 0
    already_populated = 0
    no_match = 0

    for row in lessons:
        if row.get("tech_stacks"):
            already_populated += 1
            continue

        inferred = infer_tech_stacks(row)
        if inferred:
            if dry_run:
                print(f"  WOULD UPDATE: [{row.get('category')}] {row.get('title')}")
                print(f"    -> tech_stacks: {inferred}")
            else:
                try:
                    client.table("lessons_learned").update(
                        {"tech_stacks": inferred}
                    ).eq("id", row["id"]).execute()
                    updated += 1
                except Exception as e:
                    print(f"  Error updating '{row.get('title')}': {e}")
            updated += 1 if dry_run else 0  # Count for dry_run display
        else:
            no_match += 1

    return {
        "total": len(lessons),
        "updated": updated,
        "already_populated": already_populated,
        "no_match": no_match,
    }


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    do_supabase = "--supabase" in sys.argv

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== Backfill tech_stacks ({mode}) ===\n")

    # Local
    print("--- Local (data/lessons.json) ---")
    stats = backfill_local(dry_run)
    print(f"\n  Total: {stats['total']}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Already populated: {stats['already_populated']}")
    print(f"  No match (generic): {stats['no_match']}")
    coverage = (stats["updated"] + stats["already_populated"]) / max(stats["total"], 1)
    print(f"  Coverage: {coverage:.0%}")

    # Supabase
    if do_supabase:
        print("\n--- Supabase ---")
        stats_sb = backfill_supabase(dry_run)
        print(f"\n  Total: {stats_sb['total']}")
        print(f"  Updated: {stats_sb['updated']}")
        print(f"  Already populated: {stats_sb['already_populated']}")
        print(f"  No match (generic): {stats_sb['no_match']}")
        coverage_sb = (stats_sb["updated"] + stats_sb["already_populated"]) / max(stats_sb["total"], 1)
        print(f"  Coverage: {coverage_sb:.0%}")

    print("\nDone!")


if __name__ == "__main__":
    main()
