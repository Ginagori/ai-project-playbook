# PRP: Smart Discovery

## Goal
Enrich the Discovery phase to detect similar past projects, suggest proven patterns, and ask domain-specific follow-up questions — transforming it from 5 fixed questions to an intelligent intake process.

## Why
Today `discovery_node()` asks exactly 5 hardcoded questions (project type, scale, frontend, backend, database). Every project gets the same treatment:
- A Colombian occupational health SaaS gets the same questions as a veterinary clinic
- No detection of "you've built 3 similar projects — want to reuse the pattern?"
- No domain-specific follow-ups about regulatory requirements, target users, or unique constraints
- The MemoryBridge has lessons from NOVA, KOMPLIA, KidSpark but Discovery never queries them

## What
Modify `discovery_node()` and `DISCOVERY_QUESTIONS` to:
1. After basic questions, query MemoryBridge for similar past projects
2. If similar projects found, present them and ask "Want to reuse this architecture?"
3. Add 2-3 dynamic follow-up questions based on project type (e.g., "What regulations apply?" for SaaS, "What LLM provider?" for agents)
4. Store additional context (domain, regulations, target users) in project state for use in artifact generation

## Success Criteria
- [ ] After the 5 base questions, similar projects are queried and shown (if any exist)
- [ ] If project type is `platform` or `agent`, an extra question about architecture pattern is asked
- [ ] Additional discovery context (domain keywords, regulations, target users) is stored in `ProjectState.discovery_answers`
- [ ] The planning phase can access these answers to generate domain-specific artifacts
- [ ] Existing flow still works if no past projects exist (graceful degradation)

## Context

### Must-Read Files
- `agent/orchestrator.py:44-233` — current `DISCOVERY_QUESTIONS` and `discovery_node()`
- `agent/models/project.py:78-139` — `ProjectState` model (has `user_answers` dict)
- `agent/memory_bridge.py` — MemoryBridge (from PRP 02)
- `agent/meta_learning/suggest.py:16-76` — `find_similar_projects()`

### Codebase Context
- `discovery_node()` tracks progress via `discovery_question_index` counter
- User input is processed by matching the previous question's `id`
- `ProjectState.user_answers` is an empty dict that can store arbitrary key-value pairs
- The orchestrator runs one step at a time (returns to user after each question)

### Known Gotchas
- Discovery must remain conversational — don't dump 15 questions on the user
- The `discovery_question_index` counter logic must account for dynamic questions
- `find_similar_projects()` queries local DB only — use MemoryBridge instead
- Don't make the similar project detection blocking — if Supabase is slow, skip it

### Relevant Patterns
- Follow the existing question format in `DISCOVERY_QUESTIONS` (id, question, options)
- Use `user_answers` dict for extra context (already exists but unused)

## Implementation Blueprint

### Files to Modify
- `agent/orchestrator.py` — modify `discovery_node()` and add dynamic questions
- `agent/models/project.py` — add `discovery_context` field to `ProjectState`

### Tasks

#### Task 1: Add discovery_context to ProjectState
**Files:** `agent/models/project.py`
**Pseudocode:**
```python
class ProjectState(BaseModel):
    # ... existing fields ...

    # Discovery enrichment (from Smart Discovery)
    discovery_context: dict[str, Any] = Field(default_factory=dict)
    # Keys: "domain", "regulations", "target_users", "similar_projects",
    #        "reuse_architecture", "additional_requirements"
```

#### Task 2: Add dynamic follow-up questions
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
# After DISCOVERY_QUESTIONS, add conditional questions:

FOLLOWUP_QUESTIONS = {
    "saas": [
        {
            "id": "domain",
            "question": """**Follow-up: What domain is this SaaS for?**

Examples: healthcare, education, finance, e-commerce, HR, legal, real estate...

This helps me find patterns from similar projects and generate domain-specific requirements.""",
        },
    ],
    "platform": [
        {
            "id": "architecture_pattern",
            "question": """**Follow-up: What architecture pattern?**

1. **Triple-Layer Soul + 4 Engines** — Proven in NOVA, KOMPLIA, KidSpark (recommended for AI platforms)
2. **Plugin Architecture** — Extensible system with marketplace
3. **Microservices** — Independent services communicating via API
4. **Custom** — Describe your preferred architecture

Based on past projects, option 1 has the highest success rate for AI-powered platforms.""",
            "options": {"1": "triple-layer-soul", "2": "plugin", "3": "microservices"},
        },
    ],
    "agent": [
        {
            "id": "llm_provider",
            "question": """**Follow-up: Which LLM provider?**

1. **Claude (Anthropic)** — Recommended for complex reasoning
2. **OpenAI (GPT)** — Widest ecosystem
3. **Multiple** — Multi-provider with fallback
4. **Local/Open Source** — Ollama, vLLM""",
            "options": {"1": "claude", "2": "openai", "3": "multi", "4": "local"},
        },
    ],
    "multi-agent": [
        {
            "id": "orchestration",
            "question": """**Follow-up: Orchestration pattern?**

1. **LangGraph State Machine** — Proven in Playbook, NOVA (recommended)
2. **Supervisor/Router** — Central coordinator dispatches to agents
3. **Swarm/Peer-to-peer** — Agents coordinate among themselves

Based on past projects, option 1 provides the best observability and debugging.""",
            "options": {"1": "langgraph", "2": "supervisor", "3": "swarm"},
        },
    ],
}
```

#### Task 3: Modify discovery_node to include similar project detection and follow-ups
**Files:** `agent/orchestrator.py`
**Pseudocode:**
```python
def discovery_node(state: OrchestratorState) -> OrchestratorState:
    project = state.project
    question_index = state.discovery_question_index
    user_input = state.user_input

    # --- Process answer from previous question ---
    if user_input and question_index > 0:
        # ... (existing answer processing for base questions) ...

        # Process follow-up answers
        if question_index > len(DISCOVERY_QUESTIONS):
            followup_idx = question_index - len(DISCOVERY_QUESTIONS) - 1
            pt_key = project.project_type.value if project.project_type else "saas"
            followups = FOLLOWUP_QUESTIONS.get(pt_key, [])
            if followup_idx < len(followups):
                fq = followups[followup_idx]
                answer = user_input.strip()
                if "options" in fq:
                    answer = fq["options"].get(answer, answer)
                project.discovery_context[fq["id"]] = answer

    # --- Check if ALL questions (base + followups) are done ---
    pt_key = project.project_type.value if project.project_type else None
    followups = FOLLOWUP_QUESTIONS.get(pt_key, []) if pt_key else []
    total_questions = len(DISCOVERY_QUESTIONS) + len(followups)

    # After base questions complete but before followups: show similar projects
    if question_index == len(DISCOVERY_QUESTIONS):
        # Query for similar projects
        from agent.memory_bridge import MemoryBridge
        bridge = MemoryBridge.get_instance()
        tech_stack = []
        if project.tech_stack.frontend:
            tech_stack.append(project.tech_stack.frontend)
        if project.tech_stack.backend:
            tech_stack.append(project.tech_stack.backend)

        similar = bridge.get_relevant_lessons(
            project_type=pt_key or "saas",
            tech_stack=tech_stack,
            phase="discovery",
            limit=5,
        )

        if similar:
            project.discovery_context["similar_lessons_found"] = len(similar)
            # Include similar project info in output
            similar_info = "\n".join(
                f"- **{l.title}**: {l.recommendation}"
                for l in similar[:3]
            )
            # Don't make this a blocking question — just inform
            project.discovery_context["similar_info"] = similar_info

        # If there are follow-ups, ask first one
        if followups:
            fq = followups[0]
            project.needs_user_input = True
            similar_section = ""
            if similar:
                similar_section = f"""
### Insights from Past Projects

I found {len(similar)} relevant lessons from similar projects:

{similar_info}

These will be incorporated into your project artifacts.

---

"""
            output = f"""{similar_section}{fq["question"]}"""
            return OrchestratorState(
                project=project,
                agent_output=output,
                discovery_question_index=question_index + 1,
                should_continue=True,
            )

    # --- Ask followup questions ---
    followup_idx = question_index - len(DISCOVERY_QUESTIONS) - 1
    if pt_key and 0 <= followup_idx < len(followups) - 1:
        # There's another followup to ask
        next_fq = followups[followup_idx + 1]
        project.needs_user_input = True
        return OrchestratorState(
            project=project,
            agent_output=next_fq["question"],
            discovery_question_index=question_index + 1,
            should_continue=True,
        )

    # --- All questions done → move to planning ---
    if question_index >= total_questions:
        project.current_phase = Phase.PLANNING
        project.needs_user_input = False
        # ... (existing summary generation, but now include discovery_context) ...
```

### Integration Points
- **Depends on:** PRP 02 (Memory Bridge)
- **Modifies:** `orchestrator.py` (discovery_node), `models/project.py` (ProjectState)
- **Consumed by:** PRP 04 (Enriched Planning) — uses `discovery_context` for artifact generation

## Validation Loop

### Level 1: Syntax & Style
```bash
ruff check agent/orchestrator.py agent/models/project.py --fix
ruff format agent/orchestrator.py agent/models/project.py
```

### Level 2: Type Safety
```bash
mypy agent/orchestrator.py agent/models/project.py --ignore-missing-imports
```

### Level 3: Unit Tests
```bash
.venv/Scripts/python.exe -c "
from agent.orchestrator import DISCOVERY_QUESTIONS, create_initial_state, run_orchestrator

# Test base flow still works
state = create_initial_state('Build a veterinary SaaS', 'supervised')
result = run_orchestrator(state)
assert result.agent_output is not None
assert 'Question 1' in result.agent_output
print('Base discovery flow: OK')

# Test discovery_context exists
assert hasattr(result.project, 'discovery_context')
print('discovery_context field: OK')

print('All smart discovery tests passed!')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from agent.orchestrator import run_orchestrator; print('Import OK')"
```

## Final Validation Checklist
- [ ] Base 5-question flow still works unchanged
- [ ] Follow-up questions appear after base questions (for known project types)
- [ ] Similar project detection runs without crashing (even with empty DB)
- [ ] `discovery_context` dict is populated with answers
- [ ] Existing tests don't break

## Anti-Patterns
- Do NOT make similar project detection mandatory — it's informational
- Do NOT add more than 2 follow-up questions per project type (keep it conversational)
- Do NOT change the question_index logic for base questions — only extend it
- Do NOT import MemoryBridge at module level (lazy import to avoid circular deps)
