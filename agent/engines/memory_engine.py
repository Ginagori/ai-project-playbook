"""
Memory Engine — Unified knowledge retrieval + learned preferences + auto-capture.

Responsibilities:
  - Wrap MemoryBridge for lesson retrieval (Supabase + local)
  - Manage learned team preferences (confidence-gated)
  - Auto-capture insights from project outcomes
  - Provide unified search across all knowledge sources

The Memory Engine does NOT replace MemoryBridge — it wraps it and adds
the learned preferences layer on top.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from agent.engines.base import BaseEngine
from agent.memory_bridge import MemoryBridge
from agent.meta_learning.models import LessonLearned

# Preferences stored here (local fallback when Supabase unavailable)
_PREFERENCES_FILE = Path(__file__).parent.parent.parent / "data" / "preferences.json"


class LearnedPreference(BaseModel):
    """A team-level learned preference (Layer 3 of Triple-Layer Soul)."""

    preference_type: str  # "tech_stack", "workflow", "communication", "methodology"
    content: str  # "Always use Supabase for database"
    confidence: float = 0.5  # 0.0 - 1.0
    status: str = "pending"  # "pending", "approved", "rejected"
    source_project: str = ""  # Which project taught us this
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MemoryContext(BaseModel):
    """Result of a unified memory search."""

    lessons: list[LessonLearned] = Field(default_factory=list)
    preferences: list[LearnedPreference] = Field(default_factory=list)
    similar_projects: list[dict[str, str]] = Field(default_factory=list)


class MemoryEngine(BaseEngine):
    """Archie's Memory Engine — unified knowledge retrieval."""

    _name = "memory"

    def __init__(self, supabase_client: object | None = None) -> None:
        self._supabase = supabase_client
        self._bridge: MemoryBridge | None = None
        self._preferences: list[LearnedPreference] = []
        self._initialized = False

    async def initialize(self) -> None:
        """Configure MemoryBridge and load preferences."""
        # Set up MemoryBridge (existing singleton)
        self._bridge = MemoryBridge.get_instance(self._supabase)
        if self._supabase:
            MemoryBridge.configure(self._supabase)

        # Load learned preferences from disk
        self._preferences = self._load_preferences()

        self._initialized = True

    def search(
        self,
        project_type: str,
        tech_stack: list[str],
        phase: str | None = None,
        limit: int = 10,
    ) -> MemoryContext:
        """Unified search across all knowledge sources.

        Returns lessons + active preferences + similar project info.
        """
        if not self._initialized or self._bridge is None:
            return MemoryContext()

        # Lessons from MemoryBridge
        lessons = self._bridge.get_relevant_lessons(
            project_type=project_type,
            tech_stack=tech_stack,
            phase=phase,
            limit=limit,
        )

        # Active preferences (confidence >= 0.8 or approved)
        active_prefs = self.get_active_preferences()

        # Filter preferences by relevance to tech_stack
        relevant_prefs = []
        for pref in active_prefs:
            if pref.preference_type == "tech_stack":
                # Check if any tech in stack matches preference
                pref_lower = pref.content.lower()
                if any(t.lower() in pref_lower for t in tech_stack) or not tech_stack:
                    relevant_prefs.append(pref)
            else:
                relevant_prefs.append(pref)

        return MemoryContext(
            lessons=lessons,
            preferences=relevant_prefs[:5],
        )

    def get_lessons(
        self,
        project_type: str,
        tech_stack: list[str],
        phase: str | None = None,
        limit: int = 15,
    ) -> list[LessonLearned]:
        """Get lessons from MemoryBridge (convenience delegation)."""
        if not self._initialized or self._bridge is None:
            return []
        return self._bridge.get_relevant_lessons(project_type, tech_stack, phase, limit)

    def get_gotchas(self, project_type: str, tech_stack: list[str]) -> list[str]:
        """Get gotchas from MemoryBridge (convenience delegation)."""
        if not self._initialized or self._bridge is None:
            return []
        return self._bridge.get_gotchas(project_type, tech_stack)

    def get_architecture_lessons(self, project_type: str) -> list[LessonLearned]:
        """Get architecture lessons from MemoryBridge."""
        if not self._initialized or self._bridge is None:
            return []
        return self._bridge.get_architecture_lessons(project_type)

    def get_patterns_for_feature(
        self, feature_name: str, project_type: str, tech_stack: list[str]
    ) -> list[LessonLearned]:
        """Get patterns relevant to a feature."""
        if not self._initialized or self._bridge is None:
            return []
        return self._bridge.get_patterns_for_feature(feature_name, project_type, tech_stack)

    def format_lessons(self, lessons: list[LessonLearned], format_type: str = "markdown") -> str:
        """Format lessons for injection into artifacts."""
        if not self._initialized or self._bridge is None:
            return ""
        return self._bridge.format_lessons_for_injection(lessons, format_type)

    # --- Learned Preferences ---

    def get_active_preferences(self) -> list[LearnedPreference]:
        """Get preferences that should be injected (confidence >= 0.8 or approved)."""
        return [
            p
            for p in self._preferences
            if p.status == "approved" or (p.status == "pending" and p.confidence >= 0.8)
        ]

    def get_all_preferences(self) -> list[LearnedPreference]:
        """Get all preferences (for review UI)."""
        return self._preferences.copy()

    def capture_preference(
        self,
        content: str,
        preference_type: str = "workflow",
        confidence: float = 0.5,
        source_project: str = "",
    ) -> LearnedPreference:
        """Capture a new learned preference.

        Preferences start as 'pending' and need confidence >= 0.8 or
        explicit team approval before injection.
        """
        pref = LearnedPreference(
            preference_type=preference_type,
            content=content,
            confidence=confidence,
            source_project=source_project,
        )

        # Check for duplicates
        for existing in self._preferences:
            if existing.content.lower() == content.lower():
                # Update confidence (average)
                existing.confidence = (existing.confidence + confidence) / 2
                existing.source_project = source_project or existing.source_project
                self._save_preferences()
                return existing

        self._preferences.append(pref)

        # Cap at 50 preferences (prevent bloat)
        if len(self._preferences) > 50:
            # Remove lowest-confidence pending ones
            pending = [p for p in self._preferences if p.status == "pending"]
            pending.sort(key=lambda p: p.confidence)
            if pending:
                self._preferences.remove(pending[0])

        self._save_preferences()
        return pref

    def approve_preference(self, content: str) -> bool:
        """Approve a preference (team member action)."""
        for pref in self._preferences:
            if pref.content.lower() == content.lower():
                pref.status = "approved"
                self._save_preferences()
                return True
        return False

    def reject_preference(self, content: str) -> bool:
        """Reject a preference (team member action)."""
        for pref in self._preferences:
            if pref.content.lower() == content.lower():
                pref.status = "rejected"
                self._save_preferences()
                return True
        return False

    # --- Persistence ---

    def _load_preferences(self) -> list[LearnedPreference]:
        """Load preferences from local JSON file."""
        if not _PREFERENCES_FILE.exists():
            return []
        try:
            data = json.loads(_PREFERENCES_FILE.read_text(encoding="utf-8"))
            return [LearnedPreference(**item) for item in data]
        except Exception:
            return []

    def _save_preferences(self) -> None:
        """Save preferences to local JSON file."""
        try:
            _PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)
            data = [p.model_dump() for p in self._preferences]
            _PREFERENCES_FILE.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"MemoryEngine: Failed to save preferences: {e}")
