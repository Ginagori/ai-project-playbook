"""
Agent Handoff Pattern

Allows one agent to completely hand off control to another agent.
The original agent exits and the new agent takes over.

Use case: A planner agent handing off to a coder agent after
creating the implementation plan.
"""

from typing import Callable
from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRegistry


class AgentHandoff:
    """
    Manages handoff between agents.

    The handoff pattern is useful when:
    1. Different phases require different expertise
    2. You want clean separation of concerns
    3. The receiving agent needs full autonomy

    Example:
        handoff = AgentHandoff(registry)

        # In planner agent's execute method:
        result = AgentResult(
            success=True,
            output="Plan created",
            next_agent="coder"  # Triggers handoff
        )
    """

    def __init__(self, registry: AgentRegistry):
        """
        Initialize handoff manager.

        Args:
            registry: Agent registry to look up agents
        """
        self.registry = registry
        self._handoff_history: list[dict] = []

    async def execute_with_handoff(
        self,
        initial_agent: BaseAgent,
        context: AgentContext,
        max_handoffs: int = 5,
    ) -> AgentResult:
        """
        Execute an agent with automatic handoff support.

        Args:
            initial_agent: The agent to start with
            context: Execution context
            max_handoffs: Maximum number of handoffs allowed

        Returns:
            Final result after all handoffs complete
        """
        current_agent = initial_agent
        handoff_count = 0

        while handoff_count < max_handoffs:
            # Execute current agent
            result = await current_agent.execute(context)

            # Record in history
            self._handoff_history.append({
                "agent": current_agent.name,
                "success": result.success,
                "handoff_to": result.next_agent,
            })

            # Check for handoff
            if result.next_agent is None:
                # No handoff, we're done
                return result

            # Look up next agent
            next_agent = self.registry.get(result.next_agent)
            if next_agent is None:
                result.errors.append(f"Handoff failed: agent '{result.next_agent}' not found")
                return result

            # Update context with previous result
            context.previous_results.append(result)
            context.current_iteration += 1

            # Perform handoff
            current_agent = next_agent
            handoff_count += 1

        # Max handoffs reached
        return AgentResult(
            success=False,
            output="Maximum handoffs reached",
            errors=[f"Exceeded max handoffs ({max_handoffs})"],
        )

    def get_handoff_chain(self) -> list[str]:
        """Get the chain of agents that handled the task."""
        return [h["agent"] for h in self._handoff_history]

    def clear_history(self) -> None:
        """Clear handoff history."""
        self._handoff_history = []


class HandoffTrigger:
    """
    Helper to create handoff triggers in agent results.

    Example:
        trigger = HandoffTrigger()

        # In agent's execute method:
        if needs_coding:
            return trigger.to("coder", result_data)
    """

    @staticmethod
    def to(agent_name: str, output: str = "", data: dict = None) -> AgentResult:
        """
        Create a result that triggers handoff to another agent.

        Args:
            agent_name: Name of agent to hand off to
            output: Output message from current agent
            data: Data to pass to next agent

        Returns:
            AgentResult configured for handoff
        """
        return AgentResult(
            success=True,
            output=output,
            data=data or {},
            next_agent=agent_name,
        )

    @staticmethod
    def complete(output: str, data: dict = None) -> AgentResult:
        """
        Create a result that completes without handoff.

        Args:
            output: Final output message
            data: Final data

        Returns:
            AgentResult without handoff
        """
        return AgentResult(
            success=True,
            output=output,
            data=data or {},
            next_agent=None,
        )

    @staticmethod
    def fail(error: str, output: str = "") -> AgentResult:
        """
        Create a failed result.

        Args:
            error: Error message
            output: Optional output message

        Returns:
            Failed AgentResult
        """
        return AgentResult(
            success=False,
            output=output,
            errors=[error],
            next_agent=None,
        )
