"""
Researcher Agent

Specialized agent for searching and gathering information.
Uses the playbook RAG to find relevant documentation and patterns.
"""

from agent.factory.base import BaseAgent, AgentContext, AgentResult, AgentRole
from agent.tools.playbook_rag import search_keyword, search_by_topic, get_file_content


class ResearcherAgent(BaseAgent):
    """
    Agent specialized in researching and gathering information.

    Capabilities:
    - Search the playbook for relevant patterns
    - Look up best practices
    - Find documentation
    - Gather context for other agents
    """

    def __init__(self, name: str = "researcher"):
        super().__init__(
            name=name,
            role=AgentRole.RESEARCHER,
            description="Searches and gathers information from the playbook and codebase",
            tools=[search_keyword, search_by_topic, get_file_content],
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute research task.

        Args:
            context: Context with the research task

        Returns:
            AgentResult with gathered information
        """
        task = context.task
        gathered_info = []
        sources = []

        try:
            # Strategy 1: Keyword search
            keyword_results = search_keyword(task, max_results=5)
            for result in keyword_results:
                gathered_info.append(f"**{result.title}** ({result.file})\n{result.snippet}")
                sources.append(result.file)

            # Strategy 2: Topic search for common topics
            topics_to_check = self._extract_topics(task)
            for topic in topics_to_check:
                topic_results = search_by_topic(topic)
                for result in topic_results:
                    if result.file not in sources:
                        gathered_info.append(f"**{result.title}** ({result.file})\n{result.snippet}")
                        sources.append(result.file)

            # Compile output
            if gathered_info:
                output = f"""## Research Results for: {task}

Found {len(gathered_info)} relevant sources:

{"---".join(gathered_info[:5])}

### Sources
{chr(10).join(f"- {s}" for s in sources[:5])}
"""
                return AgentResult(
                    success=True,
                    output=output,
                    data={
                        "sources": sources,
                        "result_count": len(gathered_info),
                        "task": task,
                    },
                    metadata={"agent_name": self.name},
                )
            else:
                return AgentResult(
                    success=True,
                    output=f"No specific results found for: {task}\n\nTry breaking down the task into smaller search queries.",
                    data={"sources": [], "result_count": 0},
                    metadata={"agent_name": self.name},
                )

        except Exception as e:
            return AgentResult(
                success=False,
                output=f"Research failed: {str(e)}",
                errors=[str(e)],
                metadata={"agent_name": self.name},
            )

    def _extract_topics(self, task: str) -> list[str]:
        """Extract relevant topics from task description."""
        topic_keywords = {
            "auth": ["authentication", "auth", "login", "jwt", "oauth"],
            "deployment": ["deploy", "deployment", "docker", "kubernetes", "ci/cd"],
            "testing": ["test", "testing", "pytest", "vitest", "coverage"],
            "piv loop": ["piv", "plan", "implement", "validate"],
            "architecture": ["architecture", "pattern", "structure", "vertical slice"],
            "database": ["database", "sql", "postgres", "supabase", "migration"],
            "security": ["security", "secure", "vulnerability", "xss", "injection"],
        }

        task_lower = task.lower()
        found_topics = []

        for topic, keywords in topic_keywords.items():
            if any(kw in task_lower for kw in keywords):
                found_topics.append(topic)

        return found_topics

    def can_handle(self, task: str) -> bool:
        """Check if this agent can handle the task."""
        research_keywords = [
            "find", "search", "lookup", "research", "gather",
            "what is", "how to", "best practice", "documentation",
            "learn", "understand", "explain",
        ]
        task_lower = task.lower()
        return any(kw in task_lower for kw in research_keywords)
