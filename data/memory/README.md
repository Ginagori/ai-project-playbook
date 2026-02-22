# Archie Memory — Shared Team Knowledge

This directory contains Archie's persistent memory files, shared across the team via git.

## How it works

1. **Archie** updates these files during conversations
2. **Commit + push** makes them available to the team
3. **Team members** pull to get the latest context
4. **Temporary solution** until Archie Agent has native Supabase memory

## Files

- `nivanta-ai-vision.md` — The big picture: Nivanta AI operated by 8 AI agents
- `nova-nuevo-enfoque.md` — NOVA pivot from SaaS platform to OS
- `archie-agent-state.md` — Current state of Archie Agent project
- `projects-overview.md` — Active projects and their status

## When Archie Agent is live

These files become redundant. Archie Agent will read/write directly to Supabase (pgvector) as its Memory Engine. No git pull needed.
