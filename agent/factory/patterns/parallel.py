"""
Parallel Agents Pattern (Fan-out/Fan-in)

Execute multiple agents in parallel and aggregate results.
Useful for tasks that can be decomposed into independent subtasks.

Use case: Running multiple code reviewers in parallel,
each checking different aspects (security, performance, style).
"""

import asyncio
from typing import Callable
from agent.factory.base import BaseAgent, AgentContext, AgentResult


class ParallelAgents:
    """
    Execute multiple agents in parallel.

    Example:
        parallel = ParallelAgents()
        parallel.add("security", security_reviewer)
        parallel.add("performance", performance_reviewer)
        parallel.add("style", style_reviewer)

        # Execute all in parallel
        results = await parallel.execute(context)
    """

    def __init__(
        self,
        aggregator: Callable[[list[AgentResult]], AgentResult] | None = None,
        timeout: float = 120.0,
        fail_fast: bool = False,
    ):
        """
        Initialize parallel agent executor.

        Args:
            aggregator: Function to aggregate results (default: combine all)
            timeout: Maximum time to wait for all agents
            fail_fast: If True, cancel remaining agents on first failure
        """
        self.aggregator = aggregator or self._default_aggregator
        self.timeout = timeout
        self.fail_fast = fail_fast
        self._agents: dict[str, BaseAgent] = {}

    def add(self, name: str, agent: BaseAgent) -> "ParallelAgents":
        """
        Add an agent to run in parallel.

        Args:
            name: Identifier for this agent
            agent: The agent instance

        Returns:
            Self for chaining
        """
        self._agents[name] = agent
        return self

    def remove(self, name: str) -> None:
        """Remove an agent."""
        if name in self._agents:
            del self._agents[name]

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute all agents in parallel.

        Args:
            context: Execution context (copied for each agent)

        Returns:
            Aggregated result from all agents
        """
        if not self._agents:
            return AgentResult(
                success=False,
                output="No agents to execute",
                errors=["ParallelAgents has no agents configured"],
            )

        # Create tasks for all agents
        tasks = []
        agent_names = []

        for name, agent in self._agents.items():
            # Copy context for each agent to avoid conflicts
            agent_context = AgentContext(
                task=context.task,
                project_id=context.project_id,
                previous_results=context.previous_results.copy(),
                shared_state=context.shared_state.copy(),
                max_iterations=context.max_iterations,
                current_iteration=context.current_iteration,
            )

            tasks.append(self._execute_agent(name, agent, agent_context))
            agent_names.append(name)

        # Execute all in parallel with timeout
        try:
            if self.fail_fast:
                results = await self._execute_fail_fast(tasks, agent_names)
            else:
                results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=self.timeout,
                )
        except asyncio.TimeoutError:
            return AgentResult(
                success=False,
                output="Parallel execution timed out",
                errors=[f"Timeout after {self.timeout}s"],
            )

        # Process results
        agent_results = []
        for name, result in zip(agent_names, results):
            if isinstance(result, Exception):
                agent_results.append(AgentResult(
                    success=False,
                    output=f"Agent {name} failed",
                    errors=[str(result)],
                    metadata={"agent_name": name},
                ))
            else:
                result.metadata["agent_name"] = name
                agent_results.append(result)

        # Aggregate results
        return self.aggregator(agent_results)

    async def _execute_agent(
        self,
        name: str,
        agent: BaseAgent,
        context: AgentContext,
    ) -> AgentResult:
        """Execute a single agent with error handling."""
        try:
            result = await agent.execute(context)
            result.metadata["agent_name"] = name
            return result
        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Agent {name} raised exception",
                errors=[str(e)],
                metadata={"agent_name": name},
            )

    async def _execute_fail_fast(
        self,
        tasks: list,
        agent_names: list[str],
    ) -> list[AgentResult]:
        """Execute with fail-fast behavior."""
        results = [None] * len(tasks)

        pending = set()
        for i, task in enumerate(tasks):
            pending.add(asyncio.create_task(task, name=str(i)))

        while pending:
            done, pending = await asyncio.wait(
                pending,
                timeout=self.timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                idx = int(task.get_name())
                result = task.result()
                results[idx] = result

                # Check for failure
                if not result.success and self.fail_fast:
                    # Cancel remaining tasks
                    for p in pending:
                        p.cancel()
                    # Fill remaining with cancelled
                    for i, r in enumerate(results):
                        if r is None:
                            results[i] = AgentResult(
                                success=False,
                                output="Cancelled due to fail-fast",
                                errors=["Cancelled"],
                                metadata={"agent_name": agent_names[i]},
                            )
                    return results

        return results

    def _default_aggregator(self, results: list[AgentResult]) -> AgentResult:
        """Default aggregation: combine all outputs."""
        outputs = []
        all_data = {}
        all_errors = []
        all_success = True

        for r in results:
            agent_name = r.metadata.get("agent_name", "unknown")
            outputs.append(f"## {agent_name}\n{r.output}")
            all_data[agent_name] = r.data
            all_errors.extend(r.errors)
            if not r.success:
                all_success = False

        return AgentResult(
            success=all_success,
            output="\n\n".join(outputs),
            data=all_data,
            errors=all_errors,
            metadata={
                "agent_count": len(results),
                "success_count": sum(1 for r in results if r.success),
                "failure_count": sum(1 for r in results if not r.success),
            },
        )

    def get_agents(self) -> list[str]:
        """Get list of configured agents."""
        return list(self._agents.keys())


def fan_out_fan_in(
    agents: list[BaseAgent],
    context: AgentContext,
    aggregator: Callable[[list[AgentResult]], AgentResult] | None = None,
) -> "ParallelAgents":
    """
    Convenience function to create and configure parallel execution.

    Args:
        agents: List of agents to run in parallel
        context: Execution context
        aggregator: Optional result aggregator

    Returns:
        Configured ParallelAgents instance
    """
    parallel = ParallelAgents(aggregator=aggregator)
    for i, agent in enumerate(agents):
        parallel.add(agent.name or f"agent_{i}", agent)
    return parallel
