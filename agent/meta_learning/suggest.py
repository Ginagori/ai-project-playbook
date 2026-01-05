"""
Suggestion Module

Provides recommendations based on lessons learned from previous projects.
"""

from agent.meta_learning.models import (
    LessonLearned,
    PatternMatch,
    PatternCategory,
    OutcomeType,
    get_lessons_db,
)


def find_similar_projects(
    project_type: str,
    tech_stack: list[str] | None = None,
    limit: int = 5,
) -> list[dict]:
    """
    Find similar past projects.

    Args:
        project_type: Type of project to match
        tech_stack: Optional tech stack to match
        limit: Maximum results

    Returns:
        List of similar project summaries
    """
    db = get_lessons_db()
    outcomes = db.get_outcomes(project_type=project_type)

    if not outcomes:
        # Try without project type filter
        outcomes = db.get_outcomes()

    # Score and sort by similarity
    scored = []
    for outcome in outcomes:
        score = 0.0

        # Project type match
        if outcome.project_type == project_type:
            score += 0.5

        # Tech stack overlap
        if tech_stack:
            outcome_tech = list(outcome.tech_stack.values())
            overlap = len(set(outcome_tech) & set(tech_stack))
            if outcome_tech:
                score += 0.3 * (overlap / len(outcome_tech))

        # Success bonus
        score += 0.2 * outcome.success_score

        scored.append((outcome, score))

    # Sort by score
    scored.sort(key=lambda x: x[1], reverse=True)

    return [
        {
            "project_id": o.project_id,
            "objective": o.objective,
            "project_type": o.project_type,
            "tech_stack": o.tech_stack,
            "outcome": o.outcome.value,
            "success_score": o.success_score,
            "similarity": score,
            "what_worked": o.what_worked[:3],
            "what_didnt_work": o.what_didnt_work[:3],
        }
        for o, score in scored[:limit]
    ]


def get_recommendations(
    project_type: str,
    tech_stack: list[str],
    current_phase: str | None = None,
    limit: int = 10,
) -> list[str]:
    """
    Get recommendations for a project based on learned patterns.

    Args:
        project_type: Type of project
        tech_stack: Technologies being used
        current_phase: Current phase (for phase-specific advice)
        limit: Maximum recommendations

    Returns:
        List of recommendation strings
    """
    db = get_lessons_db()
    matches = db.find_matches(project_type, tech_stack, limit=limit * 2)

    # Filter by phase if specified
    if current_phase:
        phase_categories = {
            "discovery": [PatternCategory.WORKFLOW],
            "planning": [PatternCategory.WORKFLOW, PatternCategory.ARCHITECTURE],
            "roadmap": [PatternCategory.WORKFLOW],
            "implementation": [
                PatternCategory.ARCHITECTURE,
                PatternCategory.TESTING,
                PatternCategory.TOOLING,
                PatternCategory.PITFALL,
            ],
            "deployment": [PatternCategory.DEPLOYMENT],
        }
        relevant_cats = phase_categories.get(current_phase, [])
        if relevant_cats:
            matches = [
                m for m in matches
                if m.lesson.category in relevant_cats
            ]

    recommendations = []
    seen_titles = set()

    for match in matches[:limit]:
        if match.lesson.title not in seen_titles:
            recommendations.append(match.to_recommendation())
            seen_titles.add(match.lesson.title)

    # Add default recommendations if we don't have enough
    if len(recommendations) < 3:
        defaults = _get_default_recommendations(project_type, current_phase)
        for rec in defaults:
            if len(recommendations) >= limit:
                break
            if rec not in recommendations:
                recommendations.append(rec)

    return recommendations


def suggest_tech_stack(
    project_type: str,
    requirements: list[str] | None = None,
) -> dict[str, list[str]]:
    """
    Suggest tech stack based on successful past projects.

    Args:
        project_type: Type of project
        requirements: Optional list of requirements

    Returns:
        Dict with suggested technologies by category
    """
    db = get_lessons_db()

    # Get successful outcomes for this project type
    outcomes = db.get_outcomes(project_type=project_type, outcome_type=OutcomeType.SUCCESS)

    # Count tech stack usage
    frontend_counts: dict[str, int] = {}
    backend_counts: dict[str, int] = {}
    database_counts: dict[str, int] = {}

    for outcome in outcomes:
        if outcome.tech_stack.get("frontend"):
            frontend_counts[outcome.tech_stack["frontend"]] = (
                frontend_counts.get(outcome.tech_stack["frontend"], 0) + 1
            )
        if outcome.tech_stack.get("backend"):
            backend_counts[outcome.tech_stack["backend"]] = (
                backend_counts.get(outcome.tech_stack["backend"], 0) + 1
            )
        if outcome.tech_stack.get("database"):
            database_counts[outcome.tech_stack["database"]] = (
                database_counts.get(outcome.tech_stack["database"], 0) + 1
            )

    # Sort by popularity
    suggestions = {
        "frontend": sorted(frontend_counts.keys(), key=lambda k: frontend_counts[k], reverse=True),
        "backend": sorted(backend_counts.keys(), key=lambda k: backend_counts[k], reverse=True),
        "database": sorted(database_counts.keys(), key=lambda k: database_counts[k], reverse=True),
    }

    # Add defaults if empty
    if not suggestions["frontend"]:
        suggestions["frontend"] = _get_default_tech(project_type, "frontend")
    if not suggestions["backend"]:
        suggestions["backend"] = _get_default_tech(project_type, "backend")
    if not suggestions["database"]:
        suggestions["database"] = _get_default_tech(project_type, "database")

    return suggestions


def suggest_patterns(
    project_type: str,
    category: PatternCategory,
    limit: int = 5,
) -> list[LessonLearned]:
    """
    Get pattern suggestions for a specific category.

    Args:
        project_type: Type of project
        category: Pattern category to filter
        limit: Maximum patterns

    Returns:
        List of relevant lessons
    """
    db = get_lessons_db()
    lessons = db.get_lessons(
        category=category,
        project_type=project_type,
        min_confidence=0.5,
    )

    return lessons[:limit]


def get_pitfalls_to_avoid(
    project_type: str,
    tech_stack: list[str],
) -> list[str]:
    """
    Get common pitfalls to avoid for this project context.

    Args:
        project_type: Type of project
        tech_stack: Technologies being used

    Returns:
        List of pitfall warnings
    """
    db = get_lessons_db()

    # Get pitfall lessons
    pitfalls = db.get_lessons(
        category=PatternCategory.PITFALL,
        project_type=project_type,
    )

    # Filter by relevance
    relevant = []
    for pitfall in pitfalls:
        if pitfall.matches_context(project_type, tech_stack) > 0.4:
            relevant.append(f"⚠️ **{pitfall.title}**: {pitfall.description}\n   _Avoid by: {pitfall.recommendation}_")

    # Add defaults
    if not relevant:
        relevant = [
            "⚠️ **Scope Creep**: Don't add features during implementation\n   _Avoid by: Following the roadmap strictly_",
            "⚠️ **Skipping Tests**: Don't leave testing for later\n   _Avoid by: Writing tests with each feature_",
            "⚠️ **Premature Optimization**: Don't optimize before it works\n   _Avoid by: Making it work first, then optimize_",
        ]

    return relevant


def _get_default_recommendations(project_type: str, phase: str | None) -> list[str]:
    """Get default recommendations when we don't have enough learned patterns."""
    defaults = [
        "**[General] Create CLAUDE.md First**\nDefine your project's rules before writing any code.\n_Context: Best practice for AI-assisted development_",
        "**[General] Follow PIV Loop**\nPlan → Implement → Validate for each feature.\n_Context: Systematic development workflow_",
    ]

    if phase == "implementation":
        defaults.extend([
            "**[Implementation] Write Tests Alongside Code**\nDon't leave testing for the end.\n_Context: During implementation phase_",
            "**[Implementation] Validate After Each Change**\nRun linting and tests frequently.\n_Context: Continuous validation_",
        ])
    elif phase == "planning":
        defaults.extend([
            "**[Planning] Be Specific in PRD**\nVague requirements lead to rework.\n_Context: Writing product requirements_",
        ])
    elif phase == "deployment":
        defaults.extend([
            "**[Deployment] Start with MVP Config**\nDon't over-engineer initial deployment.\n_Context: First deployment_",
        ])

    return defaults


def _get_default_tech(project_type: str, category: str) -> list[str]:
    """Get default tech suggestions based on project type."""
    defaults = {
        "saas": {
            "frontend": ["Next.js", "React", "Vue.js"],
            "backend": ["FastAPI", "Next.js API", "Express"],
            "database": ["Supabase", "PostgreSQL", "MongoDB"],
        },
        "api": {
            "frontend": [],
            "backend": ["FastAPI", "Express", "Hono"],
            "database": ["PostgreSQL", "Redis", "MongoDB"],
        },
        "agent": {
            "frontend": ["Streamlit", "Gradio"],
            "backend": ["FastAPI", "LangGraph"],
            "database": ["Supabase", "ChromaDB", "Pinecone"],
        },
        "multi_agent": {
            "frontend": ["Streamlit"],
            "backend": ["LangGraph", "FastAPI"],
            "database": ["Supabase", "PostgreSQL"],
        },
    }

    project_defaults = defaults.get(project_type, defaults["saas"])
    return project_defaults.get(category, [])
