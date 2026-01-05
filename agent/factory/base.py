"""
Base classes for Agent Factory.

Provides the foundation for all agent patterns.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable
from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Roles that specialized agents can have."""
    RESEARCHER = "researcher"      # Searches and gathers information
    CODER = "coder"               # Writes and modifies code
    REVIEWER = "reviewer"         # Reviews code and provides feedback
    PLANNER = "planner"           # Creates implementation plans
    TESTER = "tester"             # Writes and runs tests
    DEPLOYER = "deployer"         # Handles deployment tasks
    ORCHESTRATOR = "orchestrator" # Coordinates other agents


class AgentResult(BaseModel):
    """Result from an agent execution."""
    success: bool
    output: str
    data: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)
    next_agent: str | None = None  # For handoff pattern
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentContext(BaseModel):
    """Context passed between agents."""
    task: str
    project_id: str | None = None
    previous_results: list[AgentResult] = Field(default_factory=list)
    shared_state: dict[str, Any] = Field(default_factory=dict)
    max_iterations: int = 10
    current_iteration: int = 0


class BaseAgent(ABC):
    """
    Abstract base class for all agents.

    All specialized agents must inherit from this class and implement
    the execute method.
    """

    def __init__(
        self,
        name: str,
        role: AgentRole,
        description: str = "",
        tools: list[Callable] | None = None,
    ):
        self.name = name
        self.role = role
        self.description = description
        self.tools = tools or []

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's task.

        Args:
            context: The context containing task and shared state

        Returns:
            AgentResult with the execution outcome
        """
        pass

    def can_handle(self, task: str) -> bool:
        """
        Check if this agent can handle the given task.

        Override this method to implement task routing logic.
        """
        return True

    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        return f"""You are a {self.role.value} agent named {self.name}.

Your role: {self.description}

Available tools: {[t.__name__ for t in self.tools]}

Follow these principles:
1. Be precise and thorough
2. Document your reasoning
3. Ask for clarification if needed
4. Report errors clearly
"""

    def __repr__(self) -> str:
        return f"Agent({self.name}, role={self.role.value})"


class AgentRegistry:
    """
    Registry for managing available agents.

    Allows dynamic registration and lookup of agents.
    """

    def __init__(self):
        self._agents: dict[str, BaseAgent] = {}
        self._by_role: dict[AgentRole, list[BaseAgent]] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an agent."""
        self._agents[agent.name] = agent

        if agent.role not in self._by_role:
            self._by_role[agent.role] = []
        self._by_role[agent.role].append(agent)

    def get(self, name: str) -> BaseAgent | None:
        """Get an agent by name."""
        return self._agents.get(name)

    def get_by_role(self, role: AgentRole) -> list[BaseAgent]:
        """Get all agents with a specific role."""
        return self._by_role.get(role, [])

    def list_all(self) -> list[BaseAgent]:
        """List all registered agents."""
        return list(self._agents.values())

    def find_for_task(self, task: str) -> BaseAgent | None:
        """Find an agent that can handle the given task."""
        for agent in self._agents.values():
            if agent.can_handle(task):
                return agent
        return None


# Global registry instance
registry = AgentRegistry()
