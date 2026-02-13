"""
Pattern Capture Module

Extracts lessons learned from completed projects.
"""

from datetime import datetime

from agent.meta_learning.models import (
    LessonLearned,
    ProjectOutcome,
    PatternCategory,
    OutcomeType,
    get_lessons_db,
)
from agent.models.project import ProjectState, Phase


def capture_project_outcome(project: ProjectState) -> ProjectOutcome:
    """
    Capture the outcome of a completed project.

    Args:
        project: The project state to analyze

    Returns:
        ProjectOutcome with extracted metrics
    """
    # Determine outcome type
    outcome_type = _determine_outcome(project)

    # Calculate success score
    success_score = calculate_success_score(project)

    # Extract what worked and what didn't
    what_worked, what_didnt_work = _analyze_project(project)

    outcome = ProjectOutcome(
        project_id=project.id,
        objective=project.objective,
        project_type=project.project_type.value if project.project_type else "unknown",
        tech_stack={
            "frontend": project.tech_stack.frontend or "",
            "backend": project.tech_stack.backend or "",
            "database": project.tech_stack.database or "",
        },
        features_planned=[f.name for f in project.features],
        features_completed=[
            f.name for f in project.features
            if f.status == "completed"
        ],
        outcome=outcome_type,
        success_score=success_score,
        what_worked=what_worked,
        what_didnt_work=what_didnt_work,
        phases_completed=_get_completed_phases(project),
        files_created=len(project.files_created),
        started_at=project.created_at if hasattr(project, "created_at") else datetime.utcnow(),
        completed_at=datetime.utcnow(),
    )

    # Store in database
    db = get_lessons_db()
    db.add_outcome(outcome)

    # Extract patterns from this outcome
    lessons = extract_patterns(outcome, project)
    for lesson in lessons:
        db.add_lesson(lesson)

    return outcome


def calculate_success_score(project: ProjectState) -> float:
    """
    Calculate a success score for the project (0.0 to 1.0).

    Factors:
    - Feature completion rate (40%)
    - Phase progression (30%)
    - Files created (15%)
    - Generated artifacts (15%)
    """
    score = 0.0

    # Feature completion (40%)
    if project.features:
        completed = sum(1 for f in project.features if f.status == "completed")
        score += 0.4 * (completed / len(project.features))

    # Phase progression (30%)
    phase_order = [
        Phase.DISCOVERY,
        Phase.PLANNING,
        Phase.ROADMAP,
        Phase.IMPLEMENTATION,
        Phase.DEPLOYMENT,
    ]
    try:
        current_index = phase_order.index(project.current_phase)
        score += 0.3 * (current_index / (len(phase_order) - 1))
    except ValueError:
        pass

    # Files created (15%)
    files_score = min(len(project.files_created) / 10, 1.0)
    score += 0.15 * files_score

    # Generated artifacts (15%)
    artifacts = 0
    if project.claude_md:
        artifacts += 1
    if project.prd:
        artifacts += 1
    if project.deployment_configs:
        artifacts += 1
    score += 0.15 * (artifacts / 3)

    return min(score, 1.0)


def extract_patterns(outcome: ProjectOutcome, project: ProjectState) -> list[LessonLearned]:
    """
    Extract learnable patterns from a project outcome.

    Args:
        outcome: The project outcome
        project: The original project state

    Returns:
        List of lessons learned
    """
    lessons = []
    project_type = outcome.project_type
    tech_stack = list(outcome.tech_stack.values())

    # Tech stack patterns
    if outcome.success_score > 0.7:
        # Successful tech stack combination
        tech_combo = " + ".join([t for t in tech_stack if t])
        if tech_combo:
            lessons.append(LessonLearned(
                category=PatternCategory.TECH_STACK,
                title=f"Successful stack: {tech_combo}",
                description=f"This tech stack worked well for {project_type} projects",
                context=f"Building {project_type} applications",
                recommendation=f"Consider using {tech_combo} for similar projects",
                confidence=outcome.success_score,
                project_types=[project_type],
                tech_stacks=tech_stack,
                tags=["tech-stack", "success"],
            ))

    # Architecture patterns
    if project.claude_md and "vertical slice" in project.claude_md.lower():
        lessons.append(LessonLearned(
            category=PatternCategory.ARCHITECTURE,
            title="Vertical Slice Architecture",
            description="Organized code by feature rather than layer",
            context="Projects with multiple independent features",
            recommendation="Use vertical slice for feature-rich applications",
            confidence=0.8,
            project_types=[project_type],
            tags=["architecture", "vertical-slice"],
        ))

    # Workflow patterns
    if outcome.phases_completed:
        if "implementation" in outcome.phases_completed:
            if outcome.success_score > 0.6:
                lessons.append(LessonLearned(
                    category=PatternCategory.WORKFLOW,
                    title="Complete Discovery before Implementation",
                    description="Projects that completed discovery phase had better outcomes",
                    context="Starting any new project",
                    recommendation="Always complete discovery questions before coding",
                    confidence=0.85,
                    tags=["workflow", "discovery"],
                ))

    # Pitfall patterns
    for issue in outcome.what_didnt_work:
        issue_lower = issue.lower()

        if "scope" in issue_lower or "creep" in issue_lower:
            lessons.append(LessonLearned(
                category=PatternCategory.PITFALL,
                title="Scope Creep",
                description="Project scope expanded beyond original plan",
                context="During implementation phase",
                recommendation="Strictly follow the roadmap; defer new features to future iterations",
                confidence=0.75,
                tags=["pitfall", "scope"],
            ))

        if "test" in issue_lower or "coverage" in issue_lower:
            lessons.append(LessonLearned(
                category=PatternCategory.TESTING,
                title="Insufficient Test Coverage",
                description="Tests were added too late or skipped",
                context="During implementation",
                recommendation="Write tests alongside code, not after",
                confidence=0.8,
                tags=["testing", "pitfall"],
            ))

    # Deployment patterns
    if project.deployment_configs:
        scale = project.scale.value if project.scale else "mvp"
        lessons.append(LessonLearned(
            category=PatternCategory.DEPLOYMENT,
            title=f"Deployment pattern for {scale} scale",
            description=f"Generated deployment configs for {scale} environment",
            context=f"Deploying {project_type} at {scale} scale",
            recommendation="Use generated deployment configs as starting point",
            confidence=0.7,
            project_types=[project_type],
            tags=["deployment", scale],
        ))

    # Success patterns from what worked
    for success in outcome.what_worked:
        success_lower = success.lower()

        if "claude.md" in success_lower or "global rules" in success_lower:
            lessons.append(LessonLearned(
                category=PatternCategory.WORKFLOW,
                title="CLAUDE.md as Project Foundation",
                description="Having clear global rules improved development",
                context="Starting any AI-assisted project",
                recommendation="Create CLAUDE.md before writing any code",
                confidence=0.9,
                tags=["workflow", "claude-md"],
            ))

        if "prd" in success_lower or "requirements" in success_lower:
            lessons.append(LessonLearned(
                category=PatternCategory.WORKFLOW,
                title="PRD Before Implementation",
                description="Clear product requirements reduced rework",
                context="Planning phase",
                recommendation="Write comprehensive PRD before roadmap",
                confidence=0.85,
                tags=["workflow", "planning"],
            ))

    return lessons


def _determine_outcome(project: ProjectState) -> OutcomeType:
    """Determine the outcome type based on project state."""
    # Calculate completion
    if not project.features:
        return OutcomeType.ABANDONED

    completed = sum(1 for f in project.features if f.status == "completed")
    total = len(project.features)
    completion_rate = completed / total

    # Check phase
    if project.current_phase == Phase.DEPLOYMENT:
        if completion_rate > 0.8:
            return OutcomeType.SUCCESS
        else:
            return OutcomeType.PARTIAL
    elif project.current_phase in [Phase.IMPLEMENTATION, Phase.ROADMAP]:
        if completion_rate > 0.5:
            return OutcomeType.PARTIAL
        else:
            return OutcomeType.FAILED
    else:
        return OutcomeType.ABANDONED


def _analyze_project(project: ProjectState) -> tuple[list[str], list[str]]:
    """Analyze what worked and what didn't in a project."""
    what_worked = []
    what_didnt_work = []

    # Check for CLAUDE.md
    if project.claude_md:
        what_worked.append("Generated comprehensive CLAUDE.md")
    else:
        what_didnt_work.append("No CLAUDE.md generated")

    # Check for PRD
    if project.prd:
        what_worked.append("Created detailed PRD")
    else:
        what_didnt_work.append("PRD not generated")

    # Check feature completion
    completed = sum(1 for f in project.features if f.status == "completed")
    if completed == len(project.features):
        what_worked.append("All features completed")
    elif completed > 0:
        incomplete = len(project.features) - completed
        what_didnt_work.append(f"{incomplete} features not completed")
    else:
        what_didnt_work.append("No features completed")

    # Check deployment
    if project.deployment_configs:
        what_worked.append("Deployment configs generated")

    return what_worked, what_didnt_work


def _get_completed_phases(project: ProjectState) -> list[str]:
    """Get list of completed phases."""
    phase_order = [
        Phase.DISCOVERY,
        Phase.PLANNING,
        Phase.ROADMAP,
        Phase.IMPLEMENTATION,
        Phase.DEPLOYMENT,
    ]

    completed = []
    try:
        current_index = phase_order.index(project.current_phase)
        for i in range(current_index + 1):
            completed.append(phase_order[i].value)
    except ValueError:
        pass

    return completed


# =============================================================================
# Auto-Capture — extract lessons per-phase (not just at project completion)
# Inspired by OpenClaw's auto-capture triggers
# =============================================================================

def auto_capture_phase_lesson(phase: str, project: ProjectState) -> list[LessonLearned]:
    """
    Auto-capture lessons when completing a phase.

    Unlike capture_project_outcome() which runs at project end,
    this runs after each phase transition to capture incremental learning.

    Args:
        phase: The phase just completed (discovery, planning, roadmap, implementation, deployment)
        project: Current project state

    Returns:
        List of lessons captured (also stored in DB)
    """
    lessons = []
    project_type = project.project_type.value if project.project_type else "unknown"
    tech_stack = []
    if project.tech_stack.frontend:
        tech_stack.append(project.tech_stack.frontend)
    if project.tech_stack.backend:
        tech_stack.append(project.tech_stack.backend)
    if project.tech_stack.database:
        tech_stack.append(project.tech_stack.database)

    if phase == "discovery":
        # Capture tech stack choice
        if tech_stack:
            tech_combo = " + ".join(tech_stack)
            lessons.append(LessonLearned(
                category=PatternCategory.TECH_STACK,
                title=f"Tech stack chosen: {tech_combo}",
                description=f"Selected {tech_combo} for {project_type} project: {project.objective[:80]}",
                context=f"Discovery phase for {project_type}",
                recommendation=f"Consider {tech_combo} for similar {project_type} projects",
                confidence=0.6,  # Lower confidence — not proven yet
                project_types=[project_type],
                tech_stacks=tech_stack,
                tags=["tech-stack", "discovery", "auto-captured"],
            ))

    elif phase == "planning":
        # Capture architecture decisions from CLAUDE.md
        if project.claude_md:
            claude_lower = project.claude_md.lower()

            # Detect architecture pattern
            arch_patterns = {
                "vertical slice": "Vertical Slice Architecture",
                "clean architecture": "Clean Architecture",
                "plugin": "Plugin Architecture",
                "microservices": "Microservices",
                "monolith": "Monolithic Architecture",
                "event-driven": "Event-Driven Architecture",
            }
            for pattern_key, pattern_name in arch_patterns.items():
                if pattern_key in claude_lower:
                    lessons.append(LessonLearned(
                        category=PatternCategory.ARCHITECTURE,
                        title=f"Architecture: {pattern_name}",
                        description=f"Used {pattern_name} for {project_type} project",
                        context=f"Planning phase — architecture decision",
                        recommendation=f"{pattern_name} works well for {project_type} projects",
                        confidence=0.65,
                        project_types=[project_type],
                        tags=["architecture", "planning", "auto-captured"],
                    ))
                    break  # Only capture the first match

        # Capture artifact quality if available
        claude_score = project.validation_results.get("claude_md_score")
        prd_score = project.validation_results.get("prd_score")
        if claude_score is not None and prd_score is not None:
            avg_score = (claude_score + prd_score) / 2
            if avg_score >= 0.8:
                lessons.append(LessonLearned(
                    category=PatternCategory.WORKFLOW,
                    title="High-quality planning artifacts",
                    description=f"CLAUDE.md ({claude_score:.0%}) and PRD ({prd_score:.0%}) scored well",
                    context="Planning phase quality",
                    recommendation="Maintain detailed CLAUDE.md and PRD for better outcomes",
                    confidence=0.7,
                    tags=["workflow", "quality", "auto-captured"],
                ))

    elif phase == "roadmap":
        # Capture feature count and breakdown strategy
        if project.features:
            count = len(project.features)
            feature_names = [f.name for f in project.features[:5]]
            lessons.append(LessonLearned(
                category=PatternCategory.WORKFLOW,
                title=f"Roadmap: {count} features for {project_type}",
                description=f"Broke down {project_type} into {count} features: {', '.join(feature_names)}",
                context=f"Roadmap phase for {project_type}",
                recommendation=f"A {project_type} project typically needs {count} core features",
                confidence=0.55,
                project_types=[project_type],
                tags=["roadmap", "features", "auto-captured"],
            ))

    elif phase == "implementation":
        # Capture patterns used per feature
        for feature in project.features:
            if feature.status == "completed":
                plan_score = project.validation_results.get(f"plan_{feature.name}_score")
                if plan_score and plan_score >= 0.7:
                    lessons.append(LessonLearned(
                        category=PatternCategory.WORKFLOW,
                        title=f"Feature pattern: {feature.name}",
                        description=f"Successfully implemented {feature.name} for {project_type}",
                        context=f"Implementation of {feature.name}",
                        recommendation=f"Reuse the {feature.name} implementation pattern for similar projects",
                        confidence=0.6,
                        project_types=[project_type],
                        tags=["implementation", "feature-pattern", "auto-captured"],
                    ))

    elif phase == "deployment":
        # Capture deployment config choices
        if project.deployment_configs:
            scale = project.scale.value if project.scale else "mvp"
            config_types = list(project.deployment_configs.keys())
            lessons.append(LessonLearned(
                category=PatternCategory.DEPLOYMENT,
                title=f"Deployment: {scale} with {', '.join(config_types)}",
                description=f"Generated {len(config_types)} deployment configs for {scale} scale",
                context=f"Deploying {project_type} at {scale} scale",
                recommendation=f"Use {', '.join(config_types)} configs for {scale} {project_type} deployments",
                confidence=0.65,
                project_types=[project_type],
                tags=["deployment", scale, "auto-captured"],
            ))

    # Store lessons in database
    if lessons:
        db = get_lessons_db()
        for lesson in lessons:
            db.add_lesson(lesson)

    return lessons
