#!/usr/bin/env python
"""
Index the AI Project Playbook content for RAG search.

This script reads all markdown files from the playbook directory,
generates embeddings, and stores them for semantic search.

Usage:
    uv run python scripts/index_playbook.py

For Supabase storage (future):
    uv run python scripts/index_playbook.py --supabase
"""

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.progress import track

console = Console()

PLAYBOOK_DIR = Path(__file__).parent.parent / "playbook"
INDEX_FILE = Path(__file__).parent.parent / ".playbook_index.json"


def get_markdown_files() -> list[Path]:
    """Get all markdown files from the playbook directory."""
    return list(PLAYBOOK_DIR.rglob("*.md"))


def chunk_content(content: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split content into overlapping chunks for better RAG retrieval.

    Args:
        content: The full text content
        chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks

    Returns:
        List of text chunks
    """
    chunks = []
    start = 0

    while start < len(content):
        end = start + chunk_size

        # Try to break at a newline or space
        if end < len(content):
            # Look for a good break point
            break_point = content.rfind("\n\n", start, end)
            if break_point == -1:
                break_point = content.rfind("\n", start, end)
            if break_point == -1:
                break_point = content.rfind(" ", start, end)
            if break_point > start:
                end = break_point

        chunks.append(content[start:end].strip())
        start = end - overlap

    return [c for c in chunks if c]  # Filter empty chunks


def create_simple_index() -> dict:
    """
    Create a simple keyword-based index (no embeddings).

    Returns:
        Index dictionary with file paths and content chunks
    """
    index = {"files": [], "chunks": []}

    md_files = get_markdown_files()
    console.print(f"[blue]Found {len(md_files)} markdown files[/blue]")

    for file_path in track(md_files, description="Indexing files..."):
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = str(file_path.relative_to(PLAYBOOK_DIR))

            # Store file info
            index["files"].append({
                "path": relative_path,
                "title": extract_title(content),
                "size": len(content),
            })

            # Create chunks
            chunks = chunk_content(content)
            for i, chunk in enumerate(chunks):
                index["chunks"].append({
                    "file": relative_path,
                    "chunk_id": i,
                    "content": chunk,
                    "keywords": extract_keywords(chunk),
                })

        except Exception as e:
            console.print(f"[red]Error processing {file_path}: {e}[/red]")

    return index


def extract_title(content: str) -> str:
    """Extract the first heading as title."""
    for line in content.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def extract_keywords(text: str) -> list[str]:
    """Extract simple keywords from text."""
    # Simple keyword extraction - just lowercase words
    words = text.lower().split()
    # Filter short words and common words
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                  "have", "has", "had", "do", "does", "did", "will", "would", "could",
                  "should", "may", "might", "must", "shall", "can", "to", "of", "in",
                  "for", "on", "with", "at", "by", "from", "as", "into", "through",
                  "during", "before", "after", "above", "below", "between", "under",
                  "again", "further", "then", "once", "here", "there", "when", "where",
                  "why", "how", "all", "each", "few", "more", "most", "other", "some",
                  "such", "no", "nor", "not", "only", "own", "same", "so", "than",
                  "too", "very", "just", "and", "but", "if", "or", "because", "until",
                  "while", "this", "that", "these", "those", "it", "its"}

    keywords = []
    for word in words:
        # Clean the word
        clean = "".join(c for c in word if c.isalnum())
        if len(clean) > 3 and clean not in stop_words:
            keywords.append(clean)

    # Return unique keywords, limited to top 20
    return list(dict.fromkeys(keywords))[:20]


def save_index(index: dict) -> None:
    """Save the index to a JSON file."""
    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")
    console.print(f"[green]Index saved to {INDEX_FILE}[/green]")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Index the AI Project Playbook")
    parser.add_argument("--supabase", action="store_true", help="Store in Supabase (future)")
    args = parser.parse_args()

    console.print("[bold blue]AI Project Playbook Indexer[/bold blue]")
    console.print()

    if args.supabase:
        console.print("[yellow]Supabase storage not yet implemented. Using local index.[/yellow]")

    # Create and save index
    index = create_simple_index()

    console.print()
    console.print(f"[green]Indexed {len(index['files'])} files[/green]")
    console.print(f"[green]Created {len(index['chunks'])} chunks[/green]")

    save_index(index)

    console.print()
    console.print("[bold green]Indexing complete![/bold green]")


if __name__ == "__main__":
    main()
