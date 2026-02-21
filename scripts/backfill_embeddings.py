"""
Backfill embeddings for all existing Supabase lessons.

Generates semantic embeddings and updates the lessons_learned table.
Requires the 003_add_lesson_embeddings.sql migration to be run first.

Usage:
    .venv/Scripts/python.exe scripts/backfill_embeddings.py [--dry-run]
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv


def backfill(dry_run: bool = False) -> dict[str, int]:
    """Backfill embeddings for Supabase lessons that don't have one."""
    load_dotenv()

    from agent.embedding import generate_lesson_embedding, is_available

    if not is_available():
        print("Error: No embedding backend available.")
        print("Set OPENAI_API_KEY or VOYAGE_API_KEY, or ensure sentence-transformers works.")
        return {"total": 0, "updated": 0, "skipped": 0, "failed": 0}

    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    team_id = os.getenv("PLAYBOOK_TEAM_ID")

    if not all([supabase_url, supabase_key, team_id]):
        print("Error: Missing SUPABASE_URL, SUPABASE_ANON_KEY, or PLAYBOOK_TEAM_ID")
        return {"total": 0, "updated": 0, "skipped": 0, "failed": 0}

    client = create_client(supabase_url, supabase_key)

    # Fetch all lessons (only those without embeddings)
    result = (
        client.table("lessons_learned")
        .select("id, title, description, recommendation, embedding")
        .eq("team_id", team_id)
        .execute()
    )

    lessons = result.data or []
    updated = 0
    skipped = 0
    failed = 0

    for row in lessons:
        # Skip if already has embedding
        if row.get("embedding"):
            skipped += 1
            continue

        title = row.get("title", "")
        description = row.get("description", "")
        recommendation = row.get("recommendation", "")

        embedding = generate_lesson_embedding(title, description, recommendation)
        if embedding is None:
            failed += 1
            print(f"  FAILED: {title}")
            continue

        if dry_run:
            print(f"  WOULD UPDATE: {title} ({len(embedding)} dims)")
        else:
            try:
                client.table("lessons_learned").update(
                    {"embedding": embedding}
                ).eq("id", row["id"]).execute()
                updated += 1
                if updated % 10 == 0:
                    print(f"  Progress: {updated} lessons updated...")
            except Exception as e:
                failed += 1
                print(f"  ERROR updating '{title}': {e}")

        if dry_run:
            updated += 1

    return {
        "total": len(lessons),
        "updated": updated,
        "skipped": skipped,
        "failed": failed,
    }


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"=== Backfill Embeddings ({mode}) ===\n")

    stats = backfill(dry_run)

    print(f"\n  Total: {stats['total']}")
    print(f"  Updated: {stats['updated']}")
    print(f"  Already had embedding: {stats['skipped']}")
    print(f"  Failed: {stats['failed']}")

    coverage = (stats["updated"] + stats["skipped"]) / max(stats["total"], 1)
    print(f"  Coverage: {coverage:.0%}")
    print("\nDone!")


if __name__ == "__main__":
    main()
