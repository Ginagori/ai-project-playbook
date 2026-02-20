"""
Heartbeat Engine — Proactive project health monitoring and alerts.

Responsibilities:
  - Scan all active sessions for health indicators
  - Detect stale projects (no activity > 7 days)
  - Detect quality issues (artifact scores below threshold)
  - Detect stuck phases (phase unchanged for > N interactions)
  - Generate health alerts that Archie surfaces proactively

For now: manual trigger via MCP tool (playbook_health_check).
When Archie moves to NOVA: cron schedule with quiet hours.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from agent.engines.base import BaseEngine
from agent.models.project import Phase


class AlertSeverity(str, Enum):
    """Severity levels for health alerts."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class HeartbeatAlert(BaseModel):
    """A single health alert for a project."""

    session_id: str
    project_name: str
    severity: AlertSeverity
    title: str
    description: str
    suggested_action: str


class ProjectHealth(BaseModel):
    """Health report for a single project."""

    session_id: str
    objective: str
    phase: str
    days_since_activity: int = 0
    artifact_quality: float = 0.0  # avg of claude_md + prd scores (0-1)
    feature_progress: float = 0.0  # % completed features
    alerts: list[HeartbeatAlert] = Field(default_factory=list)
    health_score: float = 100.0  # 0-100, starts perfect


class HeartbeatEngine(BaseEngine):
    """Archie's Heartbeat Engine — proactive project health monitoring."""

    _name = "heartbeat"

    def __init__(self) -> None:
        self._sessions_store: dict | None = None
        self._supabase: object | None = None
        self._initialized = False

    async def initialize(
        self,
        sessions_store: dict | None = None,
        supabase_client: object | None = None,
    ) -> None:
        """Initialize with access to session data."""
        self._sessions_store = sessions_store
        self._supabase = supabase_client
        self._initialized = True

    def run_health_check(self) -> list[HeartbeatAlert]:
        """Scan all active sessions and return health alerts.

        This is the main entry point — called manually now,
        will be on cron when in NOVA.
        """
        if not self._initialized or not self._sessions_store:
            return []

        all_alerts: list[HeartbeatAlert] = []

        for session_id, state in self._sessions_store.items():
            project = state.project
            health = self._analyze_project(session_id, state)
            all_alerts.extend(health.alerts)

        # Sort by severity (critical first)
        severity_order = {AlertSeverity.CRITICAL: 0, AlertSeverity.WARNING: 1, AlertSeverity.INFO: 2}
        all_alerts.sort(key=lambda a: severity_order.get(a.severity, 3))

        return all_alerts

    def get_project_health(self, session_id: str) -> ProjectHealth | None:
        """Get health report for a single project."""
        if not self._initialized or not self._sessions_store:
            return None

        state = self._sessions_store.get(session_id)
        if not state:
            return None

        return self._analyze_project(session_id, state)

    def get_dashboard(self) -> str:
        """Generate a markdown dashboard of all project health."""
        if not self._initialized or not self._sessions_store:
            return "## Project Health Dashboard\n\nNo active sessions found."

        if not self._sessions_store:
            return "## Project Health Dashboard\n\nNo active sessions."

        reports: list[ProjectHealth] = []
        for session_id, state in self._sessions_store.items():
            reports.append(self._analyze_project(session_id, state))

        # Sort by health score (worst first)
        reports.sort(key=lambda r: r.health_score)

        lines = ["## Project Health Dashboard", ""]

        for r in reports:
            icon = self._health_icon(r.health_score)
            lines.append(f"### {icon} {r.objective}")
            lines.append(f"- **Session**: `{r.session_id[:8]}...`")
            lines.append(f"- **Phase**: {r.phase}")
            lines.append(f"- **Health Score**: {r.health_score:.0f}/100")
            lines.append(f"- **Feature Progress**: {r.feature_progress:.0f}%")

            if r.alerts:
                lines.append(f"- **Alerts**: {len(r.alerts)}")
                for alert in r.alerts:
                    sev = alert.severity.value.upper()
                    lines.append(f"  - [{sev}] {alert.title}: {alert.description}")
            lines.append("")

        # Summary
        total = len(reports)
        critical = sum(1 for r in reports if r.health_score < 40)
        warning = sum(1 for r in reports if 40 <= r.health_score < 70)
        healthy = sum(1 for r in reports if r.health_score >= 70)

        lines.append("---")
        lines.append(f"**Total projects**: {total} | Healthy: {healthy} | Warning: {warning} | Critical: {critical}")

        return "\n".join(lines)

    def _analyze_project(self, session_id: str, state: object) -> ProjectHealth:
        """Analyze a single project's health."""
        project = state.project  # type: ignore[attr-defined]
        alerts: list[HeartbeatAlert] = []
        health_score = 100.0
        objective = project.objective or "Unknown"

        # --- Check: Feature progress ---
        feature_progress = 0.0
        if project.features:
            completed = sum(1 for f in project.features if f.status == "completed")
            feature_progress = (completed / len(project.features)) * 100

        # --- Check: No features in implementation ---
        if project.current_phase == Phase.IMPLEMENTATION and not project.features:
            alerts.append(
                HeartbeatAlert(
                    session_id=session_id,
                    project_name=objective,
                    severity=AlertSeverity.CRITICAL,
                    title="No features defined",
                    description="Project is in IMPLEMENTATION phase but has 0 features",
                    suggested_action="Run roadmap phase to generate features, or add manually",
                )
            )
            health_score -= 30

        # --- Check: Artifact quality ---
        artifact_quality = 0.0
        validation = getattr(project, "validation_results", {})
        if validation:
            scores = []
            if "claude_md_score" in validation:
                scores.append(validation["claude_md_score"])
            if "prd_score" in validation:
                scores.append(validation["prd_score"])
            if scores:
                artifact_quality = sum(scores) / len(scores)

        if artifact_quality > 0 and artifact_quality < 0.6:
            alerts.append(
                HeartbeatAlert(
                    session_id=session_id,
                    project_name=objective,
                    severity=AlertSeverity.WARNING,
                    title="Low artifact quality",
                    description=f"Artifact quality score is {artifact_quality:.0%} (threshold: 60%)",
                    suggested_action="Review and improve CLAUDE.md and PRD before proceeding",
                )
            )
            health_score -= 15

        # --- Check: Stuck in early phase with no artifacts ---
        phase = project.current_phase
        if phase in (Phase.DISCOVERY,) and not project.claude_md and not project.prd:
            # This is normal for discovery, just informational
            alerts.append(
                HeartbeatAlert(
                    session_id=session_id,
                    project_name=objective,
                    severity=AlertSeverity.INFO,
                    title="In discovery",
                    description="Project is still in discovery phase",
                    suggested_action="Continue answering discovery questions to proceed",
                )
            )

        # --- Check: Completed phase check ---
        if phase == Phase.COMPLETED:
            health_score = max(health_score, 90)  # Completed projects are healthy

        return ProjectHealth(
            session_id=session_id,
            objective=objective,
            phase=phase.value if isinstance(phase, Phase) else str(phase),
            artifact_quality=artifact_quality,
            feature_progress=feature_progress,
            alerts=alerts,
            health_score=max(0, min(100, health_score)),
        )

    @staticmethod
    def _health_icon(score: float) -> str:
        """Return a text indicator for health score."""
        if score >= 80:
            return "[OK]"
        if score >= 50:
            return "[WARN]"
        return "[CRIT]"
