"""
Router Engine — Intent detection + specialized agent dispatch + output sandboxing.

Responsibilities:
  - Detect user intent from input text
  - Route to appropriate specialized agent (researcher, planner, coder, reviewer, tester)
  - Sandbox agent outputs (strip injection patterns, truncate large outputs)
  - Fall back to phase-based routing when intent is ambiguous

The Router Engine works WITH the existing LangGraph orchestrator — it doesn't
replace the phase-based flow. Instead, it provides an additional routing layer
that can dispatch to specialized agents when the user's intent goes beyond
simple phase progression.
"""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field

from agent.engines.base import BaseEngine
from agent.models.project import Phase


# Maximum output size from any agent (50KB)
MAX_OUTPUT_BYTES = 50_000

# Patterns that indicate prompt injection in agent outputs
INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)you\s+are\s+now\s+",
    r"(?i)system:\s*",
    r"(?i)IMPORTANT:\s*override",
    r"(?i)forget\s+(everything|all|your\s+instructions)",
]


class Intent(str, Enum):
    """Detected user intent for routing."""

    RESEARCH = "research"
    PLAN = "plan"
    CODE = "code"
    REVIEW = "review"
    TEST = "test"
    PHASE_CONTINUE = "continue"
    STATUS = "status"
    UNKNOWN = "unknown"


# Keyword patterns for intent detection
_INTENT_KEYWORDS: dict[Intent, list[str]] = {
    Intent.RESEARCH: ["find", "search", "lookup", "research", "what is", "how to", "explain", "investigate"],
    Intent.PLAN: ["plan", "design", "architect", "break down", "outline", "structure", "propose"],
    Intent.CODE: ["implement", "write", "code", "create", "build", "fix", "add", "generate code"],
    Intent.REVIEW: ["review", "check", "analyze", "audit", "inspect", "evaluate"],
    Intent.TEST: ["test", "verify", "validate", "coverage", "generate tests"],
    Intent.PHASE_CONTINUE: ["continue", "next", "start", "proceed", "go", "skip"],
    Intent.STATUS: ["status", "progress", "where", "state", "health", "dashboard"],
}


class RouterResult(BaseModel):
    """Result from routing a task to a specialized agent."""

    intent: Intent
    agent_used: str | None = None
    output: str = ""
    was_sanitized: bool = False
    was_truncated: bool = False
    errors: list[str] = Field(default_factory=list)


class RouterEngine(BaseEngine):
    """Archie's Router Engine — intent detection and dispatch."""

    _name = "router"

    def __init__(self) -> None:
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the router. Agents are imported on demand."""
        self._initialized = True

    def detect_intent(self, user_input: str, current_phase: Phase | None = None) -> Intent:
        """Classify user input into an Intent.

        Uses keyword matching with phase context for disambiguation.
        """
        if not user_input:
            return Intent.PHASE_CONTINUE

        text = user_input.lower().strip()

        # Exact matches for phase progression
        if text in ("continue", "next", "start", "proceed", "go", "skip", "si", "yes", "ok"):
            return Intent.PHASE_CONTINUE

        # Numeric answers (discovery phase)
        if text.isdigit() or (len(text) <= 3 and text.replace(".", "").isdigit()):
            return Intent.PHASE_CONTINUE

        # Score each intent by keyword matches
        scores: dict[Intent, float] = {intent: 0.0 for intent in Intent}

        for intent, keywords in _INTENT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    # Longer keyword matches score higher
                    scores[intent] += len(keyword.split())

        # Phase context boosts
        if current_phase == Phase.DISCOVERY:
            scores[Intent.PHASE_CONTINUE] += 1.0  # Discovery answers are usually phase progression
        elif current_phase == Phase.IMPLEMENTATION:
            scores[Intent.CODE] += 0.5  # Implementation phase favors code intent

        # Find the highest scoring intent
        best_intent = max(scores, key=lambda k: scores[k])

        if scores[best_intent] > 0:
            return best_intent

        return Intent.UNKNOWN

    async def dispatch(self, intent: Intent, task: str) -> RouterResult:
        """Route a task to the appropriate specialized agent.

        Falls back gracefully if agents are unavailable.
        """
        if not self._initialized:
            return RouterResult(intent=intent, errors=["RouterEngine not initialized"])

        agent_map: dict[Intent, str] = {
            Intent.RESEARCH: "researcher",
            Intent.PLAN: "planner",
            Intent.CODE: "coder",
            Intent.REVIEW: "reviewer",
            Intent.TEST: "tester",
        }

        agent_name = agent_map.get(intent)
        if not agent_name:
            return RouterResult(
                intent=intent,
                output="",
                agent_used=None,
            )

        try:
            # Import and execute through the existing factory system
            from agent.factory.playbook_agents import run_development_task

            result = await run_development_task(task)

            raw_output = result.get("output", "")
            sanitized = self.sandbox_output(raw_output)

            return RouterResult(
                intent=intent,
                agent_used=result.get("agent_used", agent_name),
                output=sanitized,
                was_sanitized=(sanitized != raw_output),
                was_truncated=(len(raw_output.encode("utf-8")) > MAX_OUTPUT_BYTES),
                errors=result.get("errors", []),
            )

        except Exception as e:
            return RouterResult(
                intent=intent,
                agent_used=agent_name,
                errors=[f"Agent dispatch failed: {e}"],
            )

    def sandbox_output(self, raw_output: str) -> str:
        """Sanitize agent output: strip injections, truncate if too large.

        Implements Directive 3: PROMPT INJECTION DEFENSE (output layer).
        """
        if not raw_output:
            return ""

        sanitized = raw_output

        # Strip injection patterns
        for pattern in INJECTION_PATTERNS:
            sanitized = re.sub(pattern, "[STRIPPED]", sanitized)

        # Truncate if too large
        encoded = sanitized.encode("utf-8")
        if len(encoded) > MAX_OUTPUT_BYTES:
            sanitized = encoded[:MAX_OUTPUT_BYTES].decode("utf-8", errors="ignore")
            sanitized += "\n\n[OUTPUT TRUNCATED — exceeded 50KB limit]"

        return sanitized

    def is_phase_continuation(self, user_input: str, current_phase: Phase | None = None) -> bool:
        """Quick check: is this input just a phase continuation (not a specialized task)?

        Useful for the orchestrator to decide whether to run the phase node directly
        or route through the Router Engine first.
        """
        intent = self.detect_intent(user_input, current_phase)
        return intent in (Intent.PHASE_CONTINUE, Intent.UNKNOWN)
