"""
Agent-as-Tool Pattern

Uses an agent as a callable tool for another agent.
The parent agent maintains control and can use multiple tool-agents.

Use case: A planner agent using a researcher agent to gather information
before making decisions.
"""

from typing import Callable
from agent.factory.base import BaseAgent, AgentContext, AgentResult


class AgentAsTool:
    """
    Wraps an agent to be used as a tool by another agent.

    Example:
        researcher = ResearcherAgent()
        tool = AgentAsTool(researcher)

        # Use as a tool
        result = await tool("Find best practices for authentication")
    """

    def __init__(self, agent: BaseAgent, timeout: float = 60.0):
        """
        Initialize the agent-as-tool wrapper.

        Args:
            agent: The agent to wrap as a tool
            timeout: Maximum execution time in seconds
        """
        self.agent = agent
        self.timeout = timeout
        self._call_count = 0

    @property
    def name(self) -> str:
        """Tool name for registration."""
        return f"agent_{self.agent.name}"

    @property
    def description(self) -> str:
        """Tool description for LLM."""
        return f"Delegate to {self.agent.name} ({self.agent.role.value}): {self.agent.description}"

    async def __call__(self, task: str, context: AgentContext | None = None) -> str:
        """
        Execute the wrapped agent as a tool.

        Args:
            task: The task to delegate to the agent
            context: Optional context to pass

        Returns:
            String output from the agent
        """
        self._call_count += 1

        if context is None:
            context = AgentContext(task=task)
        else:
            context.task = task

        try:
            result = await self.agent.execute(context)

            if result.success:
                return result.output
            else:
                return f"Agent failed: {'; '.join(result.errors)}"

        except Exception as e:
            return f"Agent error: {str(e)}"

    def as_function(self) -> Callable:
        """
        Return a callable function for tool registration.

        Returns:
            Async function that can be registered as a tool
        """
        async def tool_function(task: str) -> str:
            return await self(task)

        tool_function.__name__ = self.name
        tool_function.__doc__ = self.description

        return tool_function

    def get_stats(self) -> dict:
        """Get usage statistics."""
        return {
            "agent": self.agent.name,
            "role": self.agent.role.value,
            "call_count": self._call_count,
        }


class AgentToolkit:
    """
    Collection of agents wrapped as tools.

    Use this to provide multiple agent-tools to a parent agent.
    """

    def __init__(self):
        self._tools: dict[str, AgentAsTool] = {}

    def add(self, agent: BaseAgent, timeout: float = 60.0) -> None:
        """Add an agent as a tool."""
        tool = AgentAsTool(agent, timeout)
        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentAsTool | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_all_functions(self) -> list[Callable]:
        """Get all tools as callable functions."""
        return [tool.as_function() for tool in self._tools.values()]

    def get_tool_descriptions(self) -> str:
        """Get descriptions of all tools for LLM context."""
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(descriptions)

    def get_stats(self) -> dict:
        """Get usage statistics for all tools."""
        return {name: tool.get_stats() for name, tool in self._tools.items()}
