"""
Specialized Agents for AI Project Playbook

Pre-configured agents for common development tasks:
- ResearcherAgent: Searches and gathers information
- CoderAgent: Writes and modifies code
- ReviewerAgent: Reviews code and provides feedback
- PlannerAgent: Creates implementation plans
- TesterAgent: Writes and runs tests
"""

from agent.specialized.researcher import ResearcherAgent
from agent.specialized.coder import CoderAgent
from agent.specialized.reviewer import ReviewerAgent
from agent.specialized.planner import PlannerAgent
from agent.specialized.tester import TesterAgent

__all__ = [
    "ResearcherAgent",
    "CoderAgent",
    "ReviewerAgent",
    "PlannerAgent",
    "TesterAgent",
]
