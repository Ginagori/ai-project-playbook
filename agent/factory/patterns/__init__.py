"""Multi-agent patterns for the Agent Factory."""

from agent.factory.patterns.agent_as_tool import AgentAsTool
from agent.factory.patterns.handoff import AgentHandoff
from agent.factory.patterns.supervisor import SupervisorPattern
from agent.factory.patterns.parallel import ParallelAgents
from agent.factory.patterns.sequential import SequentialAgents
from agent.factory.patterns.router import LLMRouter

__all__ = [
    "AgentAsTool",
    "AgentHandoff",
    "SupervisorPattern",
    "ParallelAgents",
    "SequentialAgents",
    "LLMRouter",
]
