# System Review Guide

## What is a System Review?

A system review is a **meta-analysis of your development process** — it evaluates how well your system (CLAUDE.md, PRD, plans, validation) is working, not just whether the code runs.

> "Don't just fix the bug. Fix the system that allowed the bug." — Agentic Coding Course

The key insight: when AI-generated code has issues, the root cause is almost always in the **system** (unclear rules, missing context, vague plans), not in the AI's capability.

## When to Run a System Review

1. **After completing each phase** — Quick check before moving on
2. **After completing a project** — Full retrospective
3. **When things feel off** — Code quality declining, too many bugs
4. **Before a major milestone** — Pre-launch sanity check

## What a System Review Analyzes

### 1. Plan Fidelity

Did the implementation follow the plan?

| Check | What to Look For |
|-------|------------------|
| Feature coverage | All planned features implemented? |
| Scope adherence | No scope creep? No unplanned features? |
| Tech stack match | Using the technologies specified in CLAUDE.md? |
| Architecture match | Following the architectural pattern defined? |

### 2. Artifact Quality

Are the generated artifacts good enough?

| Artifact | Quality Indicators |
|----------|-------------------|
| **CLAUDE.md** | Has all 6 sections, specific tech stack, code patterns, architecture pattern |
| **PRD** | Has success criteria, feature prioritization, known gotchas |
| **Feature Plans** | File references, validation commands, integration points |

The AI Project Playbook Agent evaluates these automatically using rule-based checks and provides scores (0-100%).

### 3. Phase Progression

Are you moving through phases correctly?

```
[x] Discovery — Questions answered, project understood
[x] Planning — CLAUDE.md and PRD generated with good quality
[x] Roadmap — Features broken down and prioritized
[>] Implementation — PIV Loop for each feature (current)
[ ] Deployment — Configs generated for target scale
```

**Red flags:**
- Jumping to implementation without completing planning
- Spending too long in discovery (analysis paralysis)
- Skipping roadmap (implementing without a feature breakdown)

### 4. Confidence Score (1-10)

The system review calculates a weighted confidence score:

| Factor | Weight | What It Measures |
|--------|--------|-----------------|
| Phase progression | 25% | How far through the lifecycle |
| Feature completion | 30% | Percentage of features done |
| Artifact quality | 25% | CLAUDE.md + PRD + plan scores |
| Validation results | 20% | Whether artifacts pass quality checks |

**Interpretation:**
- **8-10**: High confidence — project on track
- **6-7**: Moderate — some areas need attention
- **4-5**: Low — significant issues to address
- **1-3**: Critical — major course correction needed

## How to Improve Based on Review

### If CLAUDE.md Score is Low

1. Add more specific code patterns (with actual code blocks)
2. Specify exact versions of technologies
3. Add architecture diagram or clear pattern name
4. Include testing strategy with specific frameworks

### If PRD Score is Low

1. Add measurable success criteria (checkboxes)
2. Add P0/P1 feature prioritization
3. Add "Known Gotchas" section
4. Add specific tech stack decisions

### If Feature Plans Score is Low

1. Add specific file paths to create/modify
2. Add validation commands (pytest, ruff, etc.)
3. Add integration points (what connects to what)
4. Add pseudocode for complex logic

### If Confidence Score is Low

1. Complete any skipped phases
2. Improve lowest-scoring artifacts
3. Review and update CLAUDE.md with lessons learned
4. Consider reducing scope if too ambitious

## System Review Template

```markdown
# System Review — [Project Name]

## Date: YYYY-MM-DD

## Confidence: X/10

## Plan Fidelity
- Features planned: X
- Features completed: X
- Scope changes: [list any]

## Artifact Quality
- CLAUDE.md: X%
- PRD: X%
- Plans: X% average

## What's Working
1. [thing that works well]
2. [another thing]

## What Needs Improvement
1. [issue] → [action to fix]
2. [issue] → [action to fix]

## Actions for Next Iteration
1. Update CLAUDE.md with [specific change]
2. Improve [specific artifact]
3. [next step]
```

## Using the Playbook Agent

Run a system review with the Playbook Agent:

```
playbook_system_review session_id="your-session-id"
```

Or use the slash command:

```
/system-review your-session-id
```

The agent will:
1. Analyze all artifacts and their quality scores
2. Calculate the confidence score
3. Generate specific recommendations
4. Show a detailed breakdown of each factor

## The Meta-Learning Connection

System reviews feed into the **meta-learning system**:
- Patterns from successful reviews are captured as lessons
- Future projects benefit from previous review insights
- The system literally gets better over time

This is the "improve the system" part of the PIV Loop — validation failures aren't bugs to fix, they're signals to improve your development system.
