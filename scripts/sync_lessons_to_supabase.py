"""
One-time migration: push all local lessons to Supabase.

Usage:
    .venv/Scripts/python.exe scripts/sync_lessons_to_supabase.py

This script reads all lessons from data/lessons.json and syncs them
to the Supabase lessons_learned table, deduplicating by title.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv


def migrate() -> None:
    """Sync local lessons to Supabase."""
    load_dotenv()

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    team_id = os.getenv("PLAYBOOK_TEAM_ID")

    if not all([supabase_url, supabase_key, team_id]):
        print("Error: Missing SUPABASE_URL, SUPABASE_ANON_KEY, or PLAYBOOK_TEAM_ID")
        print("Set these in your .env file")
        sys.exit(1)

    # Initialize Supabase client
    from supabase import create_client

    client = create_client(supabase_url, supabase_key)

    # Load local lessons
    lessons_file = Path(__file__).parent.parent / "data" / "lessons.json"
    if not lessons_file.exists():
        print(f"Error: {lessons_file} not found")
        sys.exit(1)

    data = json.loads(lessons_file.read_text(encoding="utf-8"))
    local_lessons = data.get("lessons", [])
    print(f"Found {len(local_lessons)} local lessons")

    # Get existing Supabase lessons for dedup
    existing_result = (
        client.table("lessons_learned")
        .select("title")
        .eq("team_id", team_id)
        .execute()
    )
    existing_titles = {
        row["title"].lower().strip() for row in (existing_result.data or [])
    }
    print(f"Found {len(existing_titles)} existing Supabase lessons")

    # Sync
    synced = 0
    skipped = 0
    errors = 0

    for lesson in local_lessons:
        title = lesson.get("title", "").strip()
        if not title:
            continue

        # Skip if already exists
        if title.lower().strip() in existing_titles:
            skipped += 1
            continue

        # Skip very low confidence (noise)
        confidence = lesson.get("confidence", 0.5)
        if confidence < 0.4:
            skipped += 1
            continue

        try:
            insert_data = {
                "team_id": team_id,
                "category": lesson.get("category", "workflow"),
                "title": title,
                "description": lesson.get("description", ""),
                "context": lesson.get("context", ""),
                "recommendation": lesson.get("recommendation", ""),
                "project_types": lesson.get("project_types", []),
                "tech_stacks": lesson.get("tech_stacks", []),
                "tags": lesson.get("tags", []),
                "confidence": confidence,
                "frequency": lesson.get("frequency", 1),
                "contributed_by": "migration-sync",
            }

            client.table("lessons_learned").insert(insert_data).execute()
            synced += 1
            existing_titles.add(title.lower().strip())  # Prevent self-duplication

        except Exception as e:
            errors += 1
            print(f"  Error syncing '{title}': {e}")

    print(f"\nDone!")
    print(f"  Synced:  {synced}")
    print(f"  Skipped: {skipped} (duplicates or low confidence)")
    print(f"  Errors:  {errors}")
    print(f"  Total in Supabase: {len(existing_titles) + synced - errors}")


if __name__ == "__main__":
    migrate()
