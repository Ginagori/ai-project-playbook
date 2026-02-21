"""
Memory Bridge — Unified lesson retrieval across Supabase and local storage.

Provides proactive lesson injection for artifact generation.
The orchestrator calls this to enrich CLAUDE.md, PRD, PRPs with real experience.

Supports hybrid retrieval: semantic similarity (via pgvector) + keyword matching.
Falls back to keyword-only when embeddings are unavailable.
"""

from agent.meta_learning.models import (
    LessonLearned,
    PatternCategory,
    get_lessons_db,
)


def _parse_lesson_row(row: dict) -> LessonLearned | None:
    """Parse a Supabase row into a LessonLearned. Returns None on failure."""
    try:
        return LessonLearned(
            category=PatternCategory(row.get("category") or "workflow"),
            title=row.get("title") or "",
            description=row.get("description") or "",
            context=row.get("context") or "",
            recommendation=row.get("recommendation") or "",
            confidence=row.get("confidence") or 0.5,
            frequency=row.get("frequency") or 1,
            project_types=row.get("project_types") or [],
            tech_stacks=row.get("tech_stacks") or [],
            tags=row.get("tags") or [],
        )
    except Exception:
        return None


class MemoryBridge:
    """
    Unified lesson retrieval from Supabase + local storage.

    Supports hybrid retrieval: semantic (pgvector) + keyword matching.

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

    # ------------------------------------------------------------------
    # Primary retrieval (hybrid: semantic + keyword)
    # ------------------------------------------------------------------

    def get_relevant_lessons(
        self,
        project_type: str,
        tech_stack: list[str],
        phase: str | None = None,
        limit: int = 15,
    ) -> list[LessonLearned]:
        """
        Get lessons relevant to this project context from ALL sources.

        1. Query local DB (keyword-based)
        2. Query Supabase — semantic first, keyword fallback
        3. Deduplicate by title
        4. Rank by hybrid score
        """
        # dict: title_lower -> (lesson, score)
        all_lessons: dict[str, tuple[LessonLearned, float]] = {}

        # --- Local lessons (keyword-based, no embeddings) ---
        try:
            local_lessons = self._local_db.get_lessons(
                project_type=project_type,
                min_confidence=0.4,
            )
            for lesson in local_lessons:
                score = lesson.matches_context(project_type, tech_stack)
                if score > 0.3:
                    all_lessons[lesson.title.lower()] = (lesson, score)
        except Exception:
            pass  # Local DB failure should not crash

        # --- Supabase lessons (semantic first, keyword fallback) ---
        if self._supabase and getattr(self._supabase, "is_configured", False):
            try:
                # Build a semantic query from the project context
                query_text = f"{project_type} project"
                if tech_stack:
                    query_text += f" using {', '.join(tech_stack)}"

                semantic_results = self._query_supabase_semantic(
                    query_text, tech_stack, limit=30,
                )

                if semantic_results:
                    for lesson, similarity in semantic_results:
                        key = lesson.title.lower()
                        metadata_score = lesson.matches_context(project_type, tech_stack)
                        hybrid_score = (
                            similarity * 0.50
                            + metadata_score * 0.30
                            + lesson.confidence * 0.20
                        )
                        if key in all_lessons:
                            existing_lesson, existing_score = all_lessons[key]
                            existing_lesson.confidence = max(
                                existing_lesson.confidence, lesson.confidence
                            )
                            existing_lesson.frequency += lesson.frequency
                            all_lessons[key] = (
                                existing_lesson,
                                max(existing_score, hybrid_score),
                            )
                        else:
                            all_lessons[key] = (lesson, hybrid_score)
                else:
                    # Fallback: keyword-based Supabase query
                    supabase_lessons = self._query_supabase_sync(
                        project_type=project_type,
                        tech_stack=tech_stack,
                    )
                    for lesson in supabase_lessons:
                        key = lesson.title.lower()
                        if key not in all_lessons:
                            score = lesson.matches_context(project_type, tech_stack)
                            all_lessons[key] = (lesson, score)
                        else:
                            existing_lesson, existing_score = all_lessons[key]
                            existing_lesson.confidence = max(
                                existing_lesson.confidence, lesson.confidence
                            )
                            existing_lesson.frequency += lesson.frequency
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
                all_lessons = {
                    k: v
                    for k, v in all_lessons.items()
                    if v[0].category in relevant_cats
                }

        # --- Effectiveness penalty ---
        for key, (lesson, score) in list(all_lessons.items()):
            eff = lesson.effectiveness_score
            if eff is not None and eff < 0.3:
                score *= 0.7  # Penalize low-effectiveness lessons
            if lesson.times_surfaced >= 10 and lesson.times_helpful == 0:
                score *= 0.5  # Heavy penalty for often-surfaced, never-helpful
            all_lessons[key] = (lesson, score)

        # --- Rank and return ---
        ranked = sorted(
            all_lessons.values(),
            key=lambda pair: pair[1],
            reverse=True,
        )
        result = [lesson for lesson, _ in ranked[:limit]]

        # --- Track surfacing (non-blocking) ---
        try:
            for lesson in result:
                lesson.times_surfaced += 1
            self._local_db._save()
        except Exception:
            pass

        return result

    # ------------------------------------------------------------------
    # Specialized retrieval
    # ------------------------------------------------------------------

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
        """Get lessons relevant to a specific feature (semantic + keyword)."""

        # Try semantic search first
        semantic_results = self._query_supabase_semantic(
            f"implementation patterns for {feature_name}",
            tech_stack,
            limit=limit * 3,
        )

        if semantic_results:
            # Merge semantic results with keyword scoring
            scored: list[tuple[LessonLearned, float]] = []
            for lesson, similarity in semantic_results:
                keyword_boost = self._keyword_score(feature_name, lesson)
                combined = similarity * 0.6 + keyword_boost * 0.4
                scored.append((lesson, combined))
            scored.sort(key=lambda x: x[1], reverse=True)
            return [lesson for lesson, _ in scored[:limit]]

        # Fallback: keyword-only matching on already-retrieved lessons
        all_lessons = self.get_relevant_lessons(project_type, tech_stack)
        scored_kw: list[tuple[LessonLearned, float]] = []
        for lesson in all_lessons:
            feature_score = self._keyword_score(feature_name, lesson)
            if feature_score > 0:
                scored_kw.append((lesson, feature_score))

        scored_kw.sort(key=lambda x: x[1], reverse=True)
        return [lesson for lesson, _ in scored_kw[:limit]]

    def semantic_search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[tuple[LessonLearned, float]]:
        """Direct semantic search — returns (lesson, similarity) pairs.

        For use by MCP tools (playbook_search_lessons).
        Falls back to keyword-based local search if semantic unavailable.
        """
        results = self._query_supabase_semantic(query, limit=limit)
        if results:
            return results

        # Fallback: keyword search on local lessons
        all_lessons = self._local_db.get_lessons(min_confidence=0.3)
        scored: list[tuple[LessonLearned, float]] = []
        for lesson in all_lessons:
            score = self._keyword_score(query, lesson)
            if score > 0:
                scored.append((lesson, min(score / 5.0, 1.0)))  # Normalize to 0-1

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # Supabase query backends
    # ------------------------------------------------------------------

    def _query_supabase_semantic(
        self,
        query_text: str,
        tech_stack: list[str] | None = None,
        limit: int = 15,
    ) -> list[tuple[LessonLearned, float]]:
        """Query Supabase using semantic similarity via match_lessons RPC.

        Returns (lesson, similarity) pairs sorted by relevance.
        Returns empty list if embeddings are unavailable or Supabase is not configured.
        """
        if not self._supabase or not getattr(self._supabase, "client", None):
            return []

        try:
            from agent.embedding import generate_query_embedding

            query_embedding = generate_query_embedding(query_text)
            if query_embedding is None:
                return []

            result = self._supabase.client.rpc("match_lessons", {
                "query_embedding": query_embedding,
                "match_team_id": self._supabase.team_id,
                "match_threshold": 0.15,
                "match_count": limit,
            }).execute()

            lessons_with_scores: list[tuple[LessonLearned, float]] = []
            for row in result.data or []:
                lesson = _parse_lesson_row(row)
                if lesson is None:
                    continue

                similarity = row.get("similarity", 0.0)

                # Post-filter: penalize tech mismatch (don't discard)
                if tech_stack and lesson.tech_stacks:
                    overlap = len(set(lesson.tech_stacks) & set(tech_stack))
                    if overlap == 0:
                        similarity *= 0.6

                lessons_with_scores.append((lesson, similarity))

            return lessons_with_scores

        except Exception as e:
            # RPC not found = migration not run yet, or other error
            if "PGRST202" not in str(e):
                print(f"MemoryBridge: Semantic query failed: {e}")
            return []

    def _query_supabase_sync(
        self,
        project_type: str,
        tech_stack: list[str],
    ) -> list[LessonLearned]:
        """Query Supabase lessons using keyword matching (original method)."""
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
                lesson = _parse_lesson_row(row)
                if lesson:
                    lessons.append(lesson)
            return lessons
        except Exception as e:
            print(f"MemoryBridge: Supabase query failed: {e}")
            return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _keyword_score(query: str, lesson: LessonLearned) -> float:
        """Score a lesson by keyword overlap with a query string."""
        query_lower = query.lower()
        title_lower = lesson.title.lower()
        desc_lower = lesson.description.lower()
        tag_str = " ".join(lesson.tags).lower()

        score = 0.0
        for word in query_lower.split():
            if len(word) < 3:
                continue
            if word in title_lower:
                score += 2.0
            if word in desc_lower:
                score += 1.0
            if word in tag_str:
                score += 0.5
        return score
