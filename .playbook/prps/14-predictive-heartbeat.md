# PRP: Predictive Gotcha Alerts

## Goal
Make the Heartbeat Engine proactive — surface relevant gotchas and warnings when a project starts or changes phase, based on the team's accumulated knowledge.

## Why
Currently the Heartbeat Engine only checks project health (stale projects, low artifact quality). It doesn't use the lesson knowledge base at all. A project using Supabase + Next.js should immediately get warned about "RLS policies need separate INSERT policies" and "Auth redirect requires middleware" — but today Archie only surfaces these if explicitly asked. The Heartbeat should proactively inject tech-stack-specific warnings at the right moment: project creation, phase transitions, and feature implementation start.

## What
1. Add `get_predictive_alerts()` to HeartbeatEngine — queries MemoryBridge for PITFALL lessons matching the project's tech stack
2. Surface predictive alerts in `playbook_health_check` dashboard
3. Add phase-aware alerts: discovery gets workflow gotchas, implementation gets architecture + pitfall gotchas
4. Surface alerts when `playbook_continue` resumes a project (gentle reminder)

## Success Criteria
- [ ] `playbook_health_check` includes "Predictive Alerts" section with tech-stack-specific gotchas
- [ ] Alerts are relevant to the project's actual tech stack (not generic)
- [ ] Phase-appropriate: implementation projects get implementation pitfalls, not discovery tips
- [ ] At least 3 relevant alerts for a typical SaaS project with Next.js + Supabase
- [ ] No false positives: alerts from irrelevant tech stacks don't appear

## Context

### Must-Read Files
- `agent/engines/heartbeat_engine.py` — Current health check logic, `_analyze_project()`, `get_dashboard()`
- `agent/memory_bridge.py` — `get_gotchas()`, `get_relevant_lessons()` with phase filtering
- `agent/models/project.py` — `ProjectModel`, `Phase`, `TechStack` definitions
- `mcp_server/playbook_mcp.py` — `playbook_health_check` tool

### Codebase Context
- HeartbeatEngine has access to `_sessions_store` (all active projects) and `_supabase`
- MemoryBridge is a singleton, can be accessed via `MemoryBridge.get_instance()`
- `get_gotchas()` returns PITFALL lessons formatted as warning strings
- `get_relevant_lessons()` accepts `phase` parameter for filtering
- HeartbeatEngine currently doesn't import or use MemoryBridge

### Known Gotchas
- HeartbeatEngine must NOT import MemoryBridge at module level (circular import risk)
- Projects in Discovery phase may not have tech_stack set yet — handle gracefully
- `project.tech_stack` may have None values for unset layers — filter them out
- Keep predictive alerts separate from health alerts (different severity, different purpose)

### Relevant Patterns
- Current `_analyze_project()` returns `ProjectHealth` with `alerts` list
- MemoryBridge phase filtering: `get_relevant_lessons(phase="implementation")`
- Gotchas formatting in MemoryBridge: `get_gotchas()` returns pre-formatted strings

## Implementation Blueprint

### Data Models
```python
# Extend HeartbeatAlert or create PredictiveAlert
class PredictiveAlert(BaseModel):
    """A proactive warning based on accumulated knowledge."""
    session_id: str
    project_name: str
    severity: AlertSeverity = AlertSeverity.INFO
    title: str
    description: str
    source_lesson: str = ""  # Which lesson generated this alert
    phase_relevant: str = ""  # Which phase this applies to
```

### Tasks

#### Task 1: Add predictive alert generation to HeartbeatEngine
**Files:** `agent/engines/heartbeat_engine.py`
**Pseudocode:**
```python
def get_predictive_alerts(self, session_id: str) -> list[HeartbeatAlert]:
    """Generate predictive alerts based on project tech stack + phase."""
    state = self._sessions_store.get(session_id)
    if not state:
        return []

    project = state.project
    tech_stack = [t for t in [
        getattr(project.tech_stack, 'frontend', None),
        getattr(project.tech_stack, 'backend', None),
        getattr(project.tech_stack, 'database', None),
    ] if t]

    if not tech_stack:
        return []

    # Import MemoryBridge locally (avoid circular import)
    from agent.memory_bridge import MemoryBridge
    bridge = MemoryBridge.get_instance()

    # Get phase-appropriate gotchas
    phase_map = {
        "discovery": "discovery",
        "planning": "planning",
        "roadmap": "roadmap",
        "implementation": "implementation",
        "deployment": "deployment",
    }
    phase_str = phase_map.get(project.current_phase.value, None)
    pt_value = project.project_type.value if project.project_type else "saas"

    gotchas = bridge.get_gotchas(pt_value, tech_stack)
    lessons = bridge.get_relevant_lessons(pt_value, tech_stack, phase=phase_str, limit=5)

    alerts = []
    # Convert gotchas to alerts
    for gotcha in gotchas[:3]:
        alerts.append(HeartbeatAlert(
            session_id=session_id,
            project_name=project.objective,
            severity=AlertSeverity.WARNING,
            title="Predictive: Known Pitfall",
            description=gotcha,
            suggested_action="Review this before proceeding",
        ))

    # Convert high-confidence lessons to info alerts
    for lesson in lessons[:3]:
        if lesson.confidence >= 0.7:
            alerts.append(HeartbeatAlert(
                session_id=session_id,
                project_name=project.objective,
                severity=AlertSeverity.INFO,
                title=f"Tip: {lesson.title}",
                description=lesson.recommendation[:200],
                suggested_action="Consider applying this pattern",
            ))

    return alerts
```

#### Task 2: Wire predictive alerts into dashboard
**Files:** `agent/engines/heartbeat_engine.py`
**Depends on:** Task 1
**Pseudocode:**
```python
def get_dashboard(self):
    # ... existing health reports ...

    # Add predictive alerts section
    lines.append("\n### Predictive Alerts (from team knowledge)")
    for session_id in self._sessions_store:
        pred_alerts = self.get_predictive_alerts(session_id)
        if pred_alerts:
            for alert in pred_alerts:
                lines.append(f"  - [{alert.severity.value.upper()}] {alert.title}")
                lines.append(f"    {alert.description[:150]}")
```

#### Task 3: Surface alerts on playbook_continue
**Files:** `mcp_server/playbook_mcp.py`
**Depends on:** Task 1
**Pseudocode:**
```python
# In playbook_continue, after loading session:
# Check if heartbeat has predictive alerts
heartbeat = _get_heartbeat_engine()
if heartbeat:
    pred_alerts = heartbeat.get_predictive_alerts(session_id)
    if pred_alerts:
        # Append gentle reminder to response
        response += "\n\n### Reminders\n"
        for alert in pred_alerts[:2]:
            response += f"- {alert.title}: {alert.description[:100]}\n"
```

### Integration Points
- **Connects to:** MemoryBridge (lesson retrieval), HeartbeatEngine (alert system)
- **Called by:** `playbook_health_check`, `playbook_continue`
- **Depends on:** Level 2 (semantic search for better gotcha retrieval)

## Validation Loop

### Level 1: Syntax & Style
```bash
.venv/Scripts/python.exe -c "
import py_compile
py_compile.compile('agent/engines/heartbeat_engine.py', doraise=True)
py_compile.compile('mcp_server/playbook_mcp.py', doraise=True)
print('Syntax OK')
"
```

### Level 2: Type Safety
```bash
.venv/Scripts/python.exe -c "
from agent.engines.heartbeat_engine import HeartbeatEngine, HeartbeatAlert
print('HeartbeatEngine imports OK')
"
```

### Level 5: Build Verification
```bash
.venv/Scripts/python.exe -c "from mcp_server.playbook_mcp import mcp; print('MCP import OK')"
```

## Final Validation Checklist
- [ ] `get_predictive_alerts()` returns tech-stack-specific alerts
- [ ] Dashboard includes predictive alerts section
- [ ] `playbook_continue` shows gentle reminders
- [ ] No alerts for projects without tech stack (discovery phase)
- [ ] Alerts are phase-appropriate
- [ ] No circular imports from HeartbeatEngine -> MemoryBridge

## Anti-Patterns
- Do NOT import MemoryBridge at module level in heartbeat_engine.py (circular import)
- Do NOT show more than 5 predictive alerts per project (noise)
- Do NOT make alerts blocking — they're informational, not errors
- Do NOT duplicate alerts that already appear in health check section
- Do NOT surface predictive alerts for completed projects
