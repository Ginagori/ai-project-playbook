"""
Meta-Learning Module

Captures patterns from completed projects and provides suggestions
based on lessons learned from previous work.
"""

from agent.meta_learning.models import (
    LessonLearned,
    ProjectOutcome,
    PatternMatch,
    PatternCategory,
    LessonsDatabase,
    get_lessons_db,
)
from agent.meta_learning.capture import (
    capture_project_outcome,
    extract_patterns,
    calculate_success_score,
    auto_capture_phase_lesson,
)
from agent.meta_learning.suggest import (
    find_similar_projects,
    get_recommendations,
    suggest_tech_stack,
    suggest_patterns,
    get_pitfalls_to_avoid,
)

__all__ = [
    # Models
    "LessonLearned",
    "ProjectOutcome",
    "PatternMatch",
    "PatternCategory",
    "LessonsDatabase",
    "get_lessons_db",
    # Capture
    "capture_project_outcome",
    "extract_patterns",
    "calculate_success_score",
    "auto_capture_phase_lesson",
    # Suggest
    "find_similar_projects",
    "get_recommendations",
    "suggest_tech_stack",
    "suggest_patterns",
    "get_pitfalls_to_avoid",
]
