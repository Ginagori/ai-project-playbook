"""
Meta-Learning Models

Data models for capturing and storing lessons learned from projects.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4
import json

from pydantic import BaseModel, Field


class OutcomeType(str, Enum):
    """Types of project outcomes."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    ABANDONED = "abandoned"


class PatternCategory(str, Enum):
    """Categories of learned patterns."""
    TECH_STACK = "tech_stack"
    ARCHITECTURE = "architecture"
    WORKFLOW = "workflow"
    TOOLING = "tooling"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    COMMUNICATION = "communication"
    PITFALL = "pitfall"  # Things to avoid


class LessonLearned(BaseModel):
    """
    A single lesson learned from a project.

    Captures what worked, what didn't, and recommendations for future projects.
    """
    id: UUID = Field(default_factory=uuid4)
    category: PatternCategory
    title: str
    description: str
    context: str  # When does this apply?
    recommendation: str  # What to do differently
    confidence: float = Field(ge=0.0, le=1.0, default=0.7)  # How confident are we?
    frequency: int = Field(default=1)  # How many times seen?
    upvotes: int = Field(default=0)
    downvotes: int = Field(default=0)

    # Effectiveness tracking
    times_surfaced: int = Field(default=0)
    times_helpful: int = Field(default=0)
    times_not_helpful: int = Field(default=0)

    # Metadata
    project_types: list[str] = Field(default_factory=list)  # Where this applies
    tech_stacks: list[str] = Field(default_factory=list)  # Related tech
    tags: list[str] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def effectiveness_score(self) -> float | None:
        """Effectiveness ratio based on user ratings. None if insufficient data."""
        total = self.times_helpful + self.times_not_helpful
        if total < 2:
            return None
        return self.times_helpful / total

    def matches_context(self, project_type: str, tech_stack: list[str]) -> float:
        """
        Calculate how well this lesson matches a given context.

        Returns a score from 0.0 to 1.0.
        """
        score = 0.0

        # Project type match
        if not self.project_types or project_type in self.project_types:
            score += 0.4

        # Tech stack overlap
        if self.tech_stacks:
            overlap = len(set(self.tech_stacks) & set(tech_stack))
            tech_score = overlap / len(self.tech_stacks) if self.tech_stacks else 0
            score += 0.4 * tech_score
        else:
            score += 0.2  # Neutral if no tech stack specified

        # Confidence and frequency boost
        score += 0.2 * self.confidence * min(self.frequency / 5, 1.0)

        return min(score, 1.0)


class ProjectOutcome(BaseModel):
    """
    Captures the outcome of a completed project.

    Used to analyze what worked and extract lessons learned.
    """
    id: UUID = Field(default_factory=uuid4)
    project_id: str
    objective: str
    project_type: str

    # What was built
    tech_stack: dict[str, str] = Field(default_factory=dict)
    features_planned: list[str] = Field(default_factory=list)
    features_completed: list[str] = Field(default_factory=list)

    # How it went
    outcome: OutcomeType = OutcomeType.SUCCESS
    success_score: float = Field(ge=0.0, le=1.0, default=0.5)

    # What happened
    what_worked: list[str] = Field(default_factory=list)
    what_didnt_work: list[str] = Field(default_factory=list)
    surprises: list[str] = Field(default_factory=list)

    # Metrics
    total_iterations: int = 0
    phases_completed: list[str] = Field(default_factory=list)
    files_created: int = 0

    # Time tracking
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    # User feedback (optional)
    user_rating: int | None = Field(ge=1, le=5, default=None)
    user_notes: str | None = None

    def calculate_completion_rate(self) -> float:
        """Calculate what percentage of features were completed."""
        if not self.features_planned:
            return 0.0
        return len(self.features_completed) / len(self.features_planned)


class PatternMatch(BaseModel):
    """
    A pattern match between a new project and learned lessons.
    """
    lesson: LessonLearned
    relevance_score: float = Field(ge=0.0, le=1.0)
    reason: str  # Why this is relevant

    def to_recommendation(self) -> str:
        """Format as a recommendation string."""
        confidence = "High" if self.relevance_score > 0.7 else "Medium" if self.relevance_score > 0.4 else "Low"
        return f"**[{confidence}] {self.lesson.title}**\n{self.lesson.recommendation}\n_Context: {self.reason}_"


class LessonsDatabase:
    """
    In-memory database for lessons learned.

    Will be replaced with Supabase in the future.
    """

    def __init__(self, storage_path: Path | None = None):
        """
        Initialize the lessons database.

        Args:
            storage_path: Optional path to persist lessons as JSON
        """
        self.storage_path = storage_path
        self._lessons: dict[UUID, LessonLearned] = {}
        self._outcomes: dict[UUID, ProjectOutcome] = {}

        # Load from storage if available
        if storage_path and storage_path.exists():
            self._load()

    def add_lesson(self, lesson: LessonLearned) -> None:
        """Add or update a lesson."""
        # Check for similar existing lesson
        similar = self._find_similar_lesson(lesson)
        if similar:
            # Update frequency and merge
            similar.frequency += 1
            similar.updated_at = datetime.utcnow()
            similar.confidence = min(similar.confidence + 0.05, 1.0)
            # Merge tags
            similar.tags = list(set(similar.tags + lesson.tags))
            similar.tech_stacks = list(set(similar.tech_stacks + lesson.tech_stacks))
        else:
            self._lessons[lesson.id] = lesson

        self._save()

    def update_lesson_confidence(self, title: str, delta: float, vote_type: str) -> LessonLearned | None:
        """Update a lesson's confidence and vote counts by title match.

        Returns the updated lesson, or None if not found.
        """
        title_lower = title.lower().strip()
        for lesson in self._lessons.values():
            if lesson.title.lower().strip() == title_lower:
                lesson.confidence = max(0.0, min(1.0, lesson.confidence + delta))
                if vote_type == "up":
                    lesson.upvotes += 1
                else:
                    lesson.downvotes += 1
                lesson.updated_at = datetime.utcnow()
                self._save()
                return lesson
        return None

    def remove_lesson(self, title: str) -> bool:
        """Remove a lesson by title match. Returns True if found and removed."""
        title_lower = title.lower().strip()
        to_remove = [
            uid for uid, lesson in self._lessons.items()
            if lesson.title.lower().strip() == title_lower
        ]
        if not to_remove:
            return False
        for uid in to_remove:
            del self._lessons[uid]
        self._save()
        return True

    def add_outcome(self, outcome: ProjectOutcome) -> None:
        """Record a project outcome."""
        self._outcomes[outcome.id] = outcome
        self._save()

    def get_lessons(
        self,
        category: PatternCategory | None = None,
        project_type: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[LessonLearned]:
        """
        Get lessons, optionally filtered.

        Args:
            category: Filter by category
            project_type: Filter by project type
            min_confidence: Minimum confidence threshold

        Returns:
            List of matching lessons
        """
        lessons = list(self._lessons.values())

        if category:
            lessons = [l for l in lessons if l.category == category]

        if project_type:
            lessons = [
                l for l in lessons
                if not l.project_types or project_type in l.project_types
            ]

        lessons = [l for l in lessons if l.confidence >= min_confidence]

        # Sort by frequency * confidence
        lessons.sort(key=lambda l: l.frequency * l.confidence, reverse=True)

        return lessons

    def get_outcomes(
        self,
        project_type: str | None = None,
        outcome_type: OutcomeType | None = None,
    ) -> list[ProjectOutcome]:
        """Get project outcomes, optionally filtered."""
        outcomes = list(self._outcomes.values())

        if project_type:
            outcomes = [o for o in outcomes if o.project_type == project_type]

        if outcome_type:
            outcomes = [o for o in outcomes if o.outcome == outcome_type]

        return outcomes

    def find_matches(
        self,
        project_type: str,
        tech_stack: list[str],
        limit: int = 5,
    ) -> list[PatternMatch]:
        """
        Find lessons that match a given project context.

        Args:
            project_type: Type of project
            tech_stack: Technologies being used
            limit: Maximum matches to return

        Returns:
            List of pattern matches with relevance scores
        """
        matches = []

        for lesson in self._lessons.values():
            score = lesson.matches_context(project_type, tech_stack)
            if score > 0.3:  # Threshold for relevance
                reason = self._generate_match_reason(lesson, project_type, tech_stack)
                matches.append(PatternMatch(
                    lesson=lesson,
                    relevance_score=score,
                    reason=reason,
                ))

        # Sort by relevance
        matches.sort(key=lambda m: m.relevance_score, reverse=True)

        return matches[:limit]

    def _find_similar_lesson(self, lesson: LessonLearned) -> LessonLearned | None:
        """Find an existing lesson that's similar."""
        for existing in self._lessons.values():
            if (existing.category == lesson.category and
                existing.title.lower() == lesson.title.lower()):
                return existing
        return None

    def _generate_match_reason(
        self,
        lesson: LessonLearned,
        project_type: str,
        tech_stack: list[str],
    ) -> str:
        """Generate a reason why this lesson matches."""
        reasons = []

        if project_type in lesson.project_types:
            reasons.append(f"applies to {project_type} projects")

        tech_overlap = set(lesson.tech_stacks) & set(tech_stack)
        if tech_overlap:
            reasons.append(f"relevant for {', '.join(tech_overlap)}")

        if lesson.frequency > 3:
            reasons.append(f"observed {lesson.frequency} times")

        if not reasons:
            reasons.append("general best practice")

        return "; ".join(reasons)

    def _save(self) -> None:
        """Save to storage."""
        if not self.storage_path:
            return

        data = {
            "lessons": [l.model_dump(mode="json") for l in self._lessons.values()],
            "outcomes": [o.model_dump(mode="json") for o in self._outcomes.values()],
        }

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)

    def _load(self) -> None:
        """Load from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[LessonsDB] Failed to read {self.storage_path}: {e}")
            return

        for i, lesson_data in enumerate(data.get("lessons", [])):
            try:
                lesson = LessonLearned(**lesson_data)
                self._lessons[lesson.id] = lesson
            except Exception as e:
                title = lesson_data.get("title", f"lesson[{i}]")
                print(f"[LessonsDB] Skipping unparseable lesson '{title}': {e}")

        for i, outcome_data in enumerate(data.get("outcomes", [])):
            try:
                outcome = ProjectOutcome(**outcome_data)
                self._outcomes[outcome.id] = outcome
            except Exception as e:
                print(f"[LessonsDB] Skipping unparseable outcome[{i}]: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get database statistics with quality metrics."""
        lessons = list(self._lessons.values())
        outcomes = list(self._outcomes.values())
        success_outcomes = [o for o in outcomes if o.outcome == OutcomeType.SUCCESS]

        total_confidence = sum(l.confidence for l in lessons)
        low_confidence = [l.title for l in lessons if l.confidence < 0.5]

        # Detect duplicates (same title, case-insensitive)
        titles = [l.title.lower().strip() for l in lessons]
        duplicates = [t for t in set(titles) if titles.count(t) > 1]

        by_category: dict[str, int] = {}
        for l in lessons:
            cat = l.category.value if hasattr(l.category, "value") else str(l.category)
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total_lessons": len(lessons),
            "total_outcomes": len(outcomes),
            "success_rate": len(success_outcomes) / len(outcomes) if outcomes else 0,
            "by_category": by_category,
            "avg_confidence": total_confidence / max(len(lessons), 1),
            "low_confidence_count": len(low_confidence),
            "low_confidence_titles": low_confidence[:10],
            "duplicate_titles": duplicates,
            "top_lessons": [
                {"title": l.title, "frequency": l.frequency}
                for l in sorted(lessons, key=lambda x: x.frequency, reverse=True)[:5]
            ],
        }


# Global database instance
_db: LessonsDatabase | None = None


def get_lessons_db(storage_path: Path | None = None) -> LessonsDatabase:
    """Get or create the global lessons database."""
    global _db
    if _db is None:
        if storage_path is None:
            # Default storage path
            storage_path = Path(__file__).parent.parent.parent / "data" / "lessons.json"
        _db = LessonsDatabase(storage_path)
    return _db
