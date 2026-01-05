"""
LLM Router Pattern

Intelligently routes tasks to the most appropriate agent based on:
1. Task content analysis
2. Agent capabilities
3. Cost optimization (use cheaper models for simpler tasks)

Use case: Routing user requests to specialized agents while
optimizing for cost and quality.
"""

from typing import Callable
from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRole


class RouteDecision:
    """Represents a routing decision."""

    def __init__(
        self,
        agent_name: str,
        confidence: float,
        reason: str,
        model_tier: str = "standard",
    ):
        self.agent_name = agent_name
        self.confidence = confidence  # 0.0 to 1.0
        self.reason = reason
        self.model_tier = model_tier  # "fast", "standard", "premium"

    def __repr__(self) -> str:
        return f"RouteDecision({self.agent_name}, confidence={self.confidence:.2f})"


class LLMRouter:
    """
    Routes tasks to appropriate agents using intelligent matching.

    Example:
        router = LLMRouter()
        router.register("researcher", researcher, keywords=["find", "search", "lookup"])
        router.register("coder", coder, keywords=["implement", "write", "code", "fix"])
        router.register("reviewer", reviewer, keywords=["review", "check", "analyze"])

        # Route a task
        decision = router.route("implement user authentication")
        result = await router.execute(context)
    """

    def __init__(
        self,
        default_agent: str | None = None,
        custom_router: Callable[[str, dict], RouteDecision] | None = None,
    ):
        """
        Initialize the router.

        Args:
            default_agent: Agent to use when no good match found
            custom_router: Optional custom routing function
        """
        self.default_agent = default_agent
        self.custom_router = custom_router
        self._agents: dict[str, BaseAgent] = {}
        self._keywords: dict[str, list[str]] = {}
        self._roles: dict[str, AgentRole] = {}
        self._tiers: dict[str, str] = {}  # model tier per agent
        self._routing_history: list[dict] = []

    def register(
        self,
        name: str,
        agent: BaseAgent,
        keywords: list[str] | None = None,
        model_tier: str = "standard",
    ) -> "LLMRouter":
        """
        Register an agent with the router.

        Args:
            name: Agent identifier
            agent: The agent instance
            keywords: Keywords that indicate this agent should handle the task
            model_tier: Cost tier ("fast", "standard", "premium")

        Returns:
            Self for chaining
        """
        self._agents[name] = agent
        self._keywords[name] = keywords or []
        self._roles[name] = agent.role
        self._tiers[name] = model_tier

        if self.default_agent is None:
            self.default_agent = name

        return self

    def unregister(self, name: str) -> None:
        """Remove an agent from the router."""
        if name in self._agents:
            del self._agents[name]
            del self._keywords[name]
            del self._roles[name]
            del self._tiers[name]

    def route(self, task: str) -> RouteDecision:
        """
        Determine which agent should handle the task.

        Args:
            task: The task description

        Returns:
            RouteDecision with chosen agent and confidence
        """
        # Use custom router if provided
        if self.custom_router:
            return self.custom_router(task, {
                "agents": self._agents,
                "keywords": self._keywords,
                "roles": self._roles,
            })

        # Default keyword-based routing
        task_lower = task.lower()
        scores: dict[str, float] = {}

        for name, keywords in self._keywords.items():
            score = 0.0
            matched_keywords = []

            for keyword in keywords:
                if keyword.lower() in task_lower:
                    score += 1.0
                    matched_keywords.append(keyword)

            # Normalize score
            if keywords:
                score = score / len(keywords)

            scores[name] = score

        # Find best match
        if scores:
            best_agent = max(scores, key=scores.get)
            best_score = scores[best_agent]

            if best_score > 0:
                return RouteDecision(
                    agent_name=best_agent,
                    confidence=min(best_score * 2, 1.0),  # Scale up for better UX
                    reason=f"Matched keywords for {best_agent}",
                    model_tier=self._tiers.get(best_agent, "standard"),
                )

        # Fall back to role-based routing
        role_decision = self._route_by_role(task_lower)
        if role_decision:
            return role_decision

        # Use default agent
        if self.default_agent:
            return RouteDecision(
                agent_name=self.default_agent,
                confidence=0.3,
                reason="Using default agent",
                model_tier=self._tiers.get(self.default_agent, "standard"),
            )

        raise ValueError("No agent available to handle task")

    def _route_by_role(self, task_lower: str) -> RouteDecision | None:
        """Route based on agent roles."""
        role_keywords = {
            AgentRole.RESEARCHER: ["find", "search", "lookup", "research", "gather", "discover"],
            AgentRole.CODER: ["implement", "write", "code", "fix", "create", "build", "develop"],
            AgentRole.REVIEWER: ["review", "check", "analyze", "audit", "inspect", "evaluate"],
            AgentRole.PLANNER: ["plan", "design", "architect", "structure", "organize"],
            AgentRole.TESTER: ["test", "verify", "validate", "qa", "quality"],
            AgentRole.DEPLOYER: ["deploy", "release", "publish", "ship", "launch"],
        }

        for role, keywords in role_keywords.items():
            for keyword in keywords:
                if keyword in task_lower:
                    # Find agent with this role
                    for name, agent_role in self._roles.items():
                        if agent_role == role:
                            return RouteDecision(
                                agent_name=name,
                                confidence=0.6,
                                reason=f"Matched role {role.value} via keyword '{keyword}'",
                                model_tier=self._tiers.get(name, "standard"),
                            )
        return None

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Route and execute the appropriate agent.

        Args:
            context: Execution context with task

        Returns:
            Result from the chosen agent
        """
        # Route the task
        decision = self.route(context.task)

        # Log routing decision
        self._routing_history.append({
            "task": context.task[:100],
            "decision": decision.agent_name,
            "confidence": decision.confidence,
            "reason": decision.reason,
        })

        # Get the agent
        agent = self._agents.get(decision.agent_name)
        if agent is None:
            return AgentResult(
                success=False,
                output="Routing error",
                errors=[f"Agent '{decision.agent_name}' not found"],
            )

        # Execute the agent
        result = await agent.execute(context)

        # Add routing metadata
        result.metadata["routing"] = {
            "chosen_agent": decision.agent_name,
            "confidence": decision.confidence,
            "reason": decision.reason,
            "model_tier": decision.model_tier,
        }

        return result

    def get_routing_history(self) -> list[dict]:
        """Get history of routing decisions."""
        return self._routing_history

    def get_agent_stats(self) -> dict:
        """Get statistics about agent usage."""
        stats = {name: 0 for name in self._agents}
        for entry in self._routing_history:
            if entry["decision"] in stats:
                stats[entry["decision"]] += 1
        return stats

    def get_registered_agents(self) -> list[str]:
        """Get list of registered agents."""
        return list(self._agents.keys())


class CostOptimizedRouter(LLMRouter):
    """
    Router that optimizes for cost by using cheaper models when possible.

    Extends LLMRouter with cost-aware routing logic.
    """

    def __init__(
        self,
        cost_threshold: float = 0.7,
        **kwargs,
    ):
        """
        Initialize cost-optimized router.

        Args:
            cost_threshold: Confidence threshold to use premium models
            **kwargs: Arguments passed to LLMRouter
        """
        super().__init__(**kwargs)
        self.cost_threshold = cost_threshold

    def route(self, task: str) -> RouteDecision:
        """Route with cost optimization."""
        decision = super().route(task)

        # Downgrade model tier for low-confidence routing
        if decision.confidence < self.cost_threshold:
            if decision.model_tier == "premium":
                decision.model_tier = "standard"
            elif decision.model_tier == "standard":
                decision.model_tier = "fast"

        return decision
