---
description: Run a system review on the current project — analyzes process quality, not code
allowed-tools: mcp__playbook__playbook_system_review, mcp__playbook__playbook_get_status, mcp__playbook__playbook_evaluate_artifact
argument-hint: session_id
---

# System Review

Run a comprehensive system review for the project session: **$ARGUMENTS**

## What to do

1. Use `playbook_system_review` with the session ID to generate the full report
2. Display the complete report to the user
3. Highlight the confidence score and top 3 recommendations
4. If confidence is below 6/10, suggest specific corrective actions

## Context

System review analyzes the **process**, not the code:
- Plan fidelity: Did we follow the plan?
- Artifact quality: Are CLAUDE.md and PRD good enough?
- Phase progression: Are we moving through phases correctly?
- Feature completion: Are features being completed?

The goal is to improve the SYSTEM that produces the code, not just fix bugs.

## Output Format

Display the full system review report, then summarize:
- Confidence score (1-10)
- Top issues found
- Recommended next actions
