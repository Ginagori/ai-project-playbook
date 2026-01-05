"""
Supervisor Pattern

A supervisor agent that dynamically orchestrates multiple worker agents.
The supervisor decides which agent to call next based on the task state.

Use case: Complex tasks that require coordination between multiple
specialized agents (researcher, coder, reviewer, tester).
"""

from typing import Callable
from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRole, AgentRegistry


class SupervisorPattern:
    """
    Supervisor that orchestrates multiple agents.

    The supervisor:
    1. Receives a task
    2. Decides which agent should handle it
    3. Delegates to that agent
    4. Reviews the result
    5. Decides next steps (another agent, complete, or fail)

    Example:
        supervisor = SupervisorPattern(registry)
        supervisor.add_worker("researcher", researcher_agent)
        supervisor.add_worker("coder", coder_agent)
        supervisor.add_worker("reviewer", reviewer_agent)

        result = await supervisor.execute(context)
    """

    def __init__(
        self,
        registry: AgentRegistry | None = None,
        max_iterations: int = 10,
        decision_fn: Callable[[AgentContext, list[AgentResult]], str | None] | None = None,
    ):
        """
        Initialize the supervisor.

        Args:
            registry: Optional agent registry to use
            max_iterations: Maximum number of agent calls
            decision_fn: Optional custom function to decide next agent
        """
        self.registry = registry or AgentRegistry()
        self.max_iterations = max_iterations
        self.decision_fn = decision_fn or self._default_decision
        self._workers: dict[str, BaseAgent] = {}
        self._execution_log: list[dict] = []

    def add_worker(self, name: str, agent: BaseAgent) -> None:
        """
        Add a worker agent to the supervisor.

        Args:
            name: Name to reference this worker
            agent: The agent instance
        """
        self._workers[name] = agent
        self.registry.register(agent)

    def remove_worker(self, name: str) -> None:
        """Remove a worker agent."""
        if name in self._workers:
            del self._workers[name]

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the supervised workflow.

        Args:
            context: Execution context with task

        Returns:
            Final aggregated result
        """
        self._execution_log = []
        iteration = 0

        while iteration < self.max_iterations:
            # Decide which agent should handle the task
            next_agent_name = self.decision_fn(context, context.previous_results)

            if next_agent_name is None:
                # No more agents needed, compile final result
                return self._compile_final_result(context)

            # Get the agent
            agent = self._workers.get(next_agent_name)
            if agent is None:
                return AgentResult(
                    success=False,
                    output="Supervisor error",
                    errors=[f"Worker '{next_agent_name}' not found"],
                )

            # Execute the agent
            result = await agent.execute(context)

            # Log execution
            self._execution_log.append({
                "iteration": iteration,
                "agent": next_agent_name,
                "success": result.success,
                "output_preview": result.output[:200] if result.output else "",
            })

            # Update context
            context.previous_results.append(result)
            context.current_iteration = iteration + 1

            # Check for failure
            if not result.success:
                # Decide if we should retry or fail
                if self._should_retry(result, iteration):
                    iteration += 1
                    continue
                else:
                    return result

            iteration += 1

        # Max iterations reached
        return AgentResult(
            success=False,
            output="Supervisor max iterations reached",
            errors=[f"Exceeded {self.max_iterations} iterations"],
        )

    def _default_decision(
        self,
        context: AgentContext,
        previous_results: list[AgentResult],
    ) -> str | None:
        """
        Default decision logic for choosing next agent.

        Override this or provide decision_fn for custom logic.
        """
        task_lower = context.task.lower()

        # No previous results - start with researcher
        if not previous_results:
            if "researcher" in self._workers:
                return "researcher"
            elif "planner" in self._workers:
                return "planner"
            else:
                # Return first available worker
                return next(iter(self._workers.keys()), None)

        # Get last result
        last_result = previous_results[-1]

        # If last agent specified next agent, use that
        if last_result.next_agent:
            return last_result.next_agent

        # Simple state machine based on what we've done
        agents_used = [r.metadata.get("agent_name") for r in previous_results if r.metadata.get("agent_name")]

        # Research -> Plan -> Code -> Review -> Test -> Done
        workflow = ["researcher", "planner", "coder", "reviewer", "tester"]

        for agent_name in workflow:
            if agent_name in self._workers and agent_name not in agents_used:
                return agent_name

        # All agents have been used, we're done
        return None

    def _should_retry(self, result: AgentResult, iteration: int) -> bool:
        """Decide if we should retry after a failure."""
        # Simple retry logic - retry once
        return iteration < 1

    def _compile_final_result(self, context: AgentContext) -> AgentResult:
        """Compile the final result from all agent outputs."""
        if not context.previous_results:
            return AgentResult(
                success=False,
                output="No agents executed",
                errors=["Supervisor completed without any agent execution"],
            )

        # Combine all outputs
        outputs = [r.output for r in context.previous_results if r.output]
        combined_output = "\n\n---\n\n".join(outputs)

        # Combine all data
        combined_data = {}
        for r in context.previous_results:
            combined_data.update(r.data)

        # Check if all succeeded
        all_success = all(r.success for r in context.previous_results)

        # Collect any errors
        all_errors = []
        for r in context.previous_results:
            all_errors.extend(r.errors)

        return AgentResult(
            success=all_success,
            output=combined_output,
            data=combined_data,
            errors=all_errors,
            metadata={
                "agents_used": len(context.previous_results),
                "execution_log": self._execution_log,
            },
        )

    def get_execution_log(self) -> list[dict]:
        """Get the execution log."""
        return self._execution_log

    def get_workers(self) -> list[str]:
        """Get list of registered workers."""
        return list(self._workers.keys())
