"""
Agent Factory - Multi-Agent Patterns for AI Project Playbook

Provides 6 patterns for orchestrating multiple AI agents:
1. Agent-as-Tool: Use an agent as a tool for another agent
2. Agent Handoff: Complete delegation to another agent
3. Supervisor: Dynamic orchestration of multiple agents
4. Parallel: Fan-out/fan-in execution
5. Sequential: Pipeline of agents
6. LLM Routing: Cost-optimized agent selection
"""

from agent.factory.base import (
    BaseAgent,
    AgentResult,
    AgentContext,
    AgentRole,
    AgentRegistry,
    registry,
)
from agent.factory.patterns import (
    AgentAsTool,
    AgentHandoff,
    SupervisorPattern,
    ParallelAgents,
    SequentialAgents,
    LLMRouter,
)

__all__ = [
    # Base classes
    "BaseAgent",
    "AgentResult",
    "AgentContext",
    "AgentRole",
    "AgentRegistry",
    "registry",
    # Patterns
    "AgentAsTool",
    "AgentHandoff",
    "SupervisorPattern",
    "ParallelAgents",
    "SequentialAgents",
    "LLMRouter",
]
