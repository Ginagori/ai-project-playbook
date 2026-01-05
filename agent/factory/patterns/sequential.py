"""
Sequential Agents Pattern (Pipeline)

Execute agents in a defined sequence, passing results from one to the next.
Each agent can transform or build upon the previous agent's output.

Use case: A pipeline where researcher -> planner -> coder -> reviewer
must run in order, each building on the previous step.
"""

from typing import Callable
from agent.factory.base import BaseAgent, AgentContext, AgentResult


class SequentialAgents:
    """
    Execute agents in sequence as a pipeline.

    Example:
        pipeline = SequentialAgents()
        pipeline.add("research", researcher)
        pipeline.add("plan", planner)
        pipeline.add("code", coder)
        pipeline.add("review", reviewer)

        # Execute in order
        result = await pipeline.execute(context)
    """

    def __init__(
        self,
        stop_on_failure: bool = True,
        transform_context: Callable[[AgentContext, AgentResult], AgentContext] | None = None,
    ):
        """
        Initialize sequential pipeline.

        Args:
            stop_on_failure: If True, stop pipeline on first failure
            transform_context: Optional function to transform context between agents
        """
        self.stop_on_failure = stop_on_failure
        self.transform_context = transform_context or self._default_transform
        self._stages: list[tuple[str, BaseAgent]] = []
        self._execution_log: list[dict] = []

    def add(self, name: str, agent: BaseAgent) -> "SequentialAgents":
        """
        Add an agent to the pipeline.

        Agents are executed in the order they are added.

        Args:
            name: Stage name
            agent: The agent instance

        Returns:
            Self for chaining
        """
        self._stages.append((name, agent))
        return self

    def insert(self, index: int, name: str, agent: BaseAgent) -> "SequentialAgents":
        """
        Insert an agent at a specific position.

        Args:
            index: Position to insert at
            name: Stage name
            agent: The agent instance

        Returns:
            Self for chaining
        """
        self._stages.insert(index, (name, agent))
        return self

    def remove(self, name: str) -> None:
        """Remove an agent by name."""
        self._stages = [(n, a) for n, a in self._stages if n != name]

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the pipeline in sequence.

        Args:
            context: Initial execution context

        Returns:
            Final result from the pipeline
        """
        if not self._stages:
            return AgentResult(
                success=False,
                output="Empty pipeline",
                errors=["SequentialAgents has no stages configured"],
            )

        self._execution_log = []
        current_context = context
        all_results: list[AgentResult] = []

        for stage_idx, (stage_name, agent) in enumerate(self._stages):
            # Execute this stage
            try:
                result = await agent.execute(current_context)
            except Exception as e:
                result = AgentResult(
                    success=False,
                    output=f"Stage {stage_name} raised exception",
                    errors=[str(e)],
                )

            # Add metadata
            result.metadata["stage_name"] = stage_name
            result.metadata["stage_index"] = stage_idx

            # Log execution
            self._execution_log.append({
                "stage": stage_name,
                "index": stage_idx,
                "success": result.success,
                "output_preview": result.output[:200] if result.output else "",
            })

            all_results.append(result)

            # Check for failure
            if not result.success and self.stop_on_failure:
                return AgentResult(
                    success=False,
                    output=f"Pipeline failed at stage: {stage_name}",
                    data={"failed_stage": stage_name, "stage_results": all_results},
                    errors=result.errors + [f"Pipeline stopped at stage {stage_idx + 1}/{len(self._stages)}"],
                    metadata={"execution_log": self._execution_log},
                )

            # Transform context for next stage
            if stage_idx < len(self._stages) - 1:
                current_context = self.transform_context(current_context, result)
                current_context.previous_results.append(result)

        # All stages complete
        return self._compile_final_result(all_results)

    def _default_transform(self, context: AgentContext, result: AgentResult) -> AgentContext:
        """
        Default context transformation between stages.

        Merges result data into shared state.
        """
        new_shared_state = context.shared_state.copy()
        new_shared_state.update(result.data)

        # Update task with any modifications from the agent
        new_task = result.data.get("next_task", context.task)

        return AgentContext(
            task=new_task,
            project_id=context.project_id,
            previous_results=context.previous_results.copy(),
            shared_state=new_shared_state,
            max_iterations=context.max_iterations,
            current_iteration=context.current_iteration + 1,
        )

    def _compile_final_result(self, results: list[AgentResult]) -> AgentResult:
        """Compile the final result from all stages."""
        # Get the last result as the primary output
        last_result = results[-1]

        # Combine all data
        combined_data = {}
        for r in results:
            stage_name = r.metadata.get("stage_name", "unknown")
            combined_data[stage_name] = r.data

        # Collect all outputs
        stage_outputs = []
        for r in results:
            stage_name = r.metadata.get("stage_name", "unknown")
            stage_outputs.append(f"### Stage: {stage_name}\n{r.output}")

        # Collect any errors
        all_errors = []
        for r in results:
            all_errors.extend(r.errors)

        # Check overall success
        all_success = all(r.success for r in results)

        return AgentResult(
            success=all_success,
            output=last_result.output,  # Use last stage's output as primary
            data={
                "final_output": last_result.data,
                "all_stages": combined_data,
            },
            errors=all_errors,
            metadata={
                "stages_completed": len(results),
                "total_stages": len(self._stages),
                "execution_log": self._execution_log,
                "stage_outputs": stage_outputs,
            },
        )

    def get_stages(self) -> list[str]:
        """Get list of stage names in order."""
        return [name for name, _ in self._stages]

    def get_execution_log(self) -> list[dict]:
        """Get the execution log."""
        return self._execution_log


class PipelineBuilder:
    """
    Fluent builder for creating sequential pipelines.

    Example:
        pipeline = (PipelineBuilder()
            .research(researcher)
            .plan(planner)
            .code(coder)
            .review(reviewer)
            .build())
    """

    def __init__(self):
        self._pipeline = SequentialAgents()

    def add(self, name: str, agent: BaseAgent) -> "PipelineBuilder":
        """Add a stage."""
        self._pipeline.add(name, agent)
        return self

    def research(self, agent: BaseAgent) -> "PipelineBuilder":
        """Add research stage."""
        return self.add("research", agent)

    def plan(self, agent: BaseAgent) -> "PipelineBuilder":
        """Add planning stage."""
        return self.add("plan", agent)

    def code(self, agent: BaseAgent) -> "PipelineBuilder":
        """Add coding stage."""
        return self.add("code", agent)

    def review(self, agent: BaseAgent) -> "PipelineBuilder":
        """Add review stage."""
        return self.add("review", agent)

    def test(self, agent: BaseAgent) -> "PipelineBuilder":
        """Add testing stage."""
        return self.add("test", agent)

    def deploy(self, agent: BaseAgent) -> "PipelineBuilder":
        """Add deployment stage."""
        return self.add("deploy", agent)

    def stop_on_failure(self, stop: bool = True) -> "PipelineBuilder":
        """Configure stop on failure behavior."""
        self._pipeline.stop_on_failure = stop
        return self

    def build(self) -> SequentialAgents:
        """Build and return the pipeline."""
        return self._pipeline
