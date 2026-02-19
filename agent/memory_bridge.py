"""
Memory Bridge — Unified lesson retrieval across Supabase and local storage.

Provides proactive lesson injection for artifact generation.
The orchestrator calls this to enrich CLAUDE.md, PRD, PRPs with real experience.
"""

from agent.meta_learning.models import (
    LessonLearned,
    PatternCategory,
    get_lessons_db,
)


class MemoryBridge:
    """
    Unified lesson retrieval from Supabase + local storage.

    Usage:
        bridge = MemoryBridge.get_instance()
        lessons = bridge.get_relevant_lessons("saas", ["nextjs", "supabase"])
        gotchas = bridge.get_gotchas("saas", ["nextjs", "supabase"])
    """

    _instance: "MemoryBridge | None" = None

    def __init__(self, supabase_client=None):  # type: ignore[no-untyped-def]
        self._supabase = supabase_client
        self._local_db = get_lessons_db()

    @classmethod
    def get_instance(cls, supabase_client=None) -> "MemoryBridge":  # type: ignore[no-untyped-def]
        """Get or create the singleton instance."""
        if cls._instance is None:
            cls._instance = cls(supabase_client)
        return cls._instance

    @classmethod
    def configure(cls, supabase_client) -> None:  # type: ignore[no-untyped-def]
        """Configure with Supabase client (called at MCP startup)."""
        instance = cls.get_instance()
        instance._supabase = supabase_client

    def get_relevant_lessons(
        self,
        project_type: str,
        tech_stack: list[str],
        phase: str | None = None,
        limit: int = 15,
    ) -> list[LessonLearned]:
        """
        Get lessons relevant to this project context from ALL sources.

        1. Query local DB
        2. Query Supabase (if configured)
        3. Deduplicate by title
        4. Rank by relevance * confidence
        """
        all_lessons: dict[str, LessonLearned] = {}

        # --- Local lessons ---
        try:
            local_lessons = self._local_db.get_lessons(
                project_type=project_type,
                min_confidence=0.4,
            )
            for lesson in local_lessons:
                score = lesson.matches_context(project_type, tech_stack)
                if score > 0.3:
                    all_lessons[lesson.title.lower()] = lesson
        except Exception:
            pass  # Local DB failure should not crash

        # --- Supabase lessons ---
        if self._supabase and getattr(self._supabase, "is_configured", False):
            try:
                supabase_lessons = self._query_supabase_sync(
                    project_type=project_type,
                    tech_stack=tech_stack,
                )
                for lesson in supabase_lessons:
                    key = lesson.title.lower()
                    if key not in all_lessons:
                        all_lessons[key] = lesson
                    else:
                        # Merge: keep higher confidence, sum frequencies
                        existing = all_lessons[key]
                        existing.confidence = max(existing.confidence, lesson.confidence)
                        existing.frequency += lesson.frequency
            except Exception:
                pass  # Supabase failure should not crash

        # --- Filter by phase if specified ---
        if phase:
            phase_categories: dict[str, list[PatternCategory]] = {
                "discovery": [PatternCategory.WORKFLOW, PatternCategory.TECH_STACK],
                "planning": [
                    PatternCategory.WORKFLOW,
                    PatternCategory.ARCHITECTURE,
                ],
                "roadmap": [PatternCategory.WORKFLOW],
                "implementation": [
                    PatternCategory.ARCHITECTURE,
                    PatternCategory.TESTING,
                    PatternCategory.TOOLING,
                    PatternCategory.PITFALL,
                ],
                "deployment": [PatternCategory.DEPLOYMENT],
            }
            relevant_cats = phase_categories.get(phase, [])
            if relevant_cats:
                all_lessons = {k: v for k, v in all_lessons.items() if v.category in relevant_cats}

        # --- Rank and return ---
        ranked = sorted(
            all_lessons.values(),
            key=lambda ls: ls.matches_context(project_type, tech_stack) * ls.confidence,
            reverse=True,
        )
        return ranked[:limit]

    def get_gotchas(
        self,
        project_type: str,
        tech_stack: list[str],
        limit: int = 5,
    ) -> list[str]:
        """Get known gotchas formatted as warning strings."""
        lessons = self.get_relevant_lessons(project_type, tech_stack)
        pitfalls = [ls for ls in lessons if ls.category == PatternCategory.PITFALL]

        gotchas = []
        for p in pitfalls[:limit]:
            gotchas.append(f"- **{p.title}**: {p.description} \u2192 {p.recommendation}")
        return gotchas

    def get_architecture_lessons(
        self,
        project_type: str,
        limit: int = 5,
    ) -> list[LessonLearned]:
        """Get architecture-specific lessons."""
        lessons = self.get_relevant_lessons(project_type, [])
        return [ls for ls in lessons if ls.category == PatternCategory.ARCHITECTURE][:limit]

    def get_patterns_for_feature(
        self,
        feature_name: str,
        project_type: str,
        tech_stack: list[str],
        limit: int = 3,
    ) -> list[LessonLearned]:
        """Get lessons relevant to a specific feature."""
        all_lessons = self.get_relevant_lessons(project_type, tech_stack)
        feature_lower = feature_name.lower()

        # Score by feature keyword match
        scored: list[tuple[LessonLearned, float]] = []
        for lesson in all_lessons:
            title_lower = lesson.title.lower()
            desc_lower = lesson.description.lower()
            tag_str = " ".join(lesson.tags).lower()

            feature_score = 0.0
            for word in feature_lower.split():
                if len(word) < 3:
                    continue
                if word in title_lower:
                    feature_score += 2.0
                if word in desc_lower:
                    feature_score += 1.0
                if word in tag_str:
                    feature_score += 0.5

            if feature_score > 0:
                scored.append((lesson, feature_score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return [lesson for lesson, _ in scored[:limit]]

    def format_lessons_for_injection(
        self,
        lessons: list[LessonLearned],
        format_type: str = "markdown",
    ) -> str:
        """Format lessons as markdown for injection into artifacts."""
        if not lessons:
            return ""

        if format_type == "gotchas":
            lines = ["### Known Gotchas (from past projects)", ""]
            for lesson in lessons:
                lines.append(f"- **{lesson.title}**: {lesson.recommendation}")
            return "\n".join(lines)

        if format_type == "patterns":
            lines = ["### Learned Patterns", ""]
            for lesson in lessons:
                conf = f"{lesson.confidence:.0%}"
                freq = f"seen {lesson.frequency}x" if lesson.frequency > 1 else "new"
                lines.append(f"- **{lesson.title}** ({conf}, {freq}): {lesson.recommendation}")
            return "\n".join(lines)

        # Default: full markdown
        lines = ["### Lessons from Past Projects", ""]
        for lesson in lessons:
            lines.append(f"**{lesson.title}** [{lesson.category.value}]")
            lines.append(f"  {lesson.description}")
            lines.append(f"  \u2192 {lesson.recommendation}")
            lines.append("")
        return "\n".join(lines)

    def _query_supabase_sync(
        self,
        project_type: str,
        tech_stack: list[str],
    ) -> list[LessonLearned]:
        """Query Supabase lessons synchronously."""
        if not self._supabase or not self._supabase.client:
            return []

        try:
            query = self._supabase.client.table("lessons_learned").select("*")

            if self._supabase.team_id:
                query = query.eq("team_id", self._supabase.team_id)

            if project_type:
                query = query.contains("project_types", [project_type])

            if tech_stack:
                query = query.overlaps("tech_stacks", tech_stack)

            result = query.order("confidence", desc=True).limit(50).execute()

            lessons = []
            for row in result.data or []:
                try:
                    lessons.append(
                        LessonLearned(
                            category=PatternCategory(row.get("category", "workflow")),
                            title=row.get("title", ""),
                            description=row.get("description", ""),
                            context=row.get("context", ""),
                            recommendation=row.get("recommendation", ""),
                            confidence=row.get("confidence", 0.5),
                            frequency=row.get("frequency", 1),
                            project_types=row.get("project_types", []),
                            tech_stacks=row.get("tech_stacks", []),
                            tags=row.get("tags", []),
                        )
                    )
                except Exception:
                    continue  # Skip malformed rows
            return lessons
        except Exception as e:
            print(f"MemoryBridge: Supabase query failed: {e}")
            return []
