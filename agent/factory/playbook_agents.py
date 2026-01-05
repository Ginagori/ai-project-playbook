"""
Playbook Agents - Pre-configured agent setups for the AI Project Playbook.

Provides ready-to-use agent configurations for common workflows:
- Development Pipeline: Research -> Plan -> Code -> Review -> Test
- Code Review: Parallel reviewers (security, quality, style)
- Feature Implementation: Supervised multi-agent workflow
"""

from agent.factory.base import AgentRegistry, AgentContext
from agent.factory.patterns import (
    SupervisorPattern,
    ParallelAgents,
    SequentialAgents,
    LLMRouter,
)
from agent.specialized import (
    ResearcherAgent,
    CoderAgent,
    ReviewerAgent,
    PlannerAgent,
    TesterAgent,
)


def create_development_pipeline() -> SequentialAgents:
    """
    Create a sequential pipeline for feature development.

    Pipeline: Research -> Plan -> Code -> Review -> Test

    Returns:
        Configured SequentialAgents instance
    """
    pipeline = SequentialAgents(stop_on_failure=True)

    pipeline.add("research", ResearcherAgent())
    pipeline.add("plan", PlannerAgent())
    pipeline.add("code", CoderAgent())
    pipeline.add("review", ReviewerAgent())
    pipeline.add("test", TesterAgent())

    return pipeline


def create_code_review_parallel() -> ParallelAgents:
    """
    Create parallel code reviewers.

    Runs multiple review checks in parallel for faster feedback.

    Returns:
        Configured ParallelAgents instance
    """
    parallel = ParallelAgents(fail_fast=False)

    # Could add more specialized reviewers here
    parallel.add("quality", ReviewerAgent("quality_reviewer"))
    parallel.add("security", ReviewerAgent("security_reviewer"))

    return parallel


def create_feature_supervisor() -> SupervisorPattern:
    """
    Create a supervised workflow for feature implementation.

    The supervisor coordinates agents based on task requirements.

    Returns:
        Configured SupervisorPattern instance
    """
    registry = AgentRegistry()
    supervisor = SupervisorPattern(registry=registry, max_iterations=10)

    # Register all agents
    supervisor.add_worker("researcher", ResearcherAgent())
    supervisor.add_worker("planner", PlannerAgent())
    supervisor.add_worker("coder", CoderAgent())
    supervisor.add_worker("reviewer", ReviewerAgent())
    supervisor.add_worker("tester", TesterAgent())

    return supervisor


def create_task_router() -> LLMRouter:
    """
    Create a router that directs tasks to appropriate agents.

    Uses keyword matching to route tasks to the best agent.

    Returns:
        Configured LLMRouter instance
    """
    router = LLMRouter(default_agent="researcher")

    router.register(
        "researcher",
        ResearcherAgent(),
        keywords=["find", "search", "lookup", "research", "what is", "how to"],
        model_tier="fast",
    )

    router.register(
        "planner",
        PlannerAgent(),
        keywords=["plan", "design", "architect", "break down", "outline"],
        model_tier="standard",
    )

    router.register(
        "coder",
        CoderAgent(),
        keywords=["implement", "write", "code", "create", "build", "fix"],
        model_tier="standard",
    )

    router.register(
        "reviewer",
        ReviewerAgent(),
        keywords=["review", "check", "analyze", "audit", "inspect"],
        model_tier="standard",
    )

    router.register(
        "tester",
        TesterAgent(),
        keywords=["test", "verify", "validate", "coverage"],
        model_tier="fast",
    )

    return router


# =============================================================================
# Pre-configured instances for easy access
# =============================================================================

# Default pipeline for feature development
default_pipeline = create_development_pipeline()

# Default router for task delegation
default_router = create_task_router()

# Default supervisor for complex workflows
default_supervisor = create_feature_supervisor()


async def run_development_task(task: str) -> dict:
    """
    Run a development task through the appropriate agent.

    Automatically routes the task to the best agent.

    Args:
        task: The task description

    Returns:
        Result dictionary with output and metadata
    """
    context = AgentContext(task=task)
    result = await default_router.execute(context)

    return {
        "success": result.success,
        "output": result.output,
        "agent_used": result.metadata.get("routing", {}).get("chosen_agent"),
        "errors": result.errors,
    }


async def run_feature_pipeline(feature: str) -> dict:
    """
    Run a feature through the full development pipeline.

    Goes through: Research -> Plan -> Code -> Review -> Test

    Args:
        feature: The feature description

    Returns:
        Result dictionary with outputs from all stages
    """
    context = AgentContext(task=feature)
    result = await default_pipeline.execute(context)

    return {
        "success": result.success,
        "output": result.output,
        "stages_completed": result.metadata.get("stages_completed", 0),
        "execution_log": result.metadata.get("execution_log", []),
        "errors": result.errors,
    }
