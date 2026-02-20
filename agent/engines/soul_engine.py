"""
Soul Engine — Core Soul integrity + context assembly for artifact generation.

Responsibilities:
  - Verify Core Soul hash at initialization (3-layer protection)
  - Build structured context blocks for each orchestrator phase
  - Validate that outputs don't leak IP or violate directives
  - Provide Archie's identity (personality, language, methodology)

Unlike Frank's SoulEngine (which builds LLM system prompts), Archie's SoulEngine
builds *context blocks* that enrich artifact generation. Archie works through
Claude Code via MCP — his "prompt" is the /archie skill file.
"""

from __future__ import annotations

import re

from agent.core_soul import CORE_SOUL, get_core_soul, verify_core_soul
from agent.engines.base import BaseEngine


# Patterns that should NEVER appear in Archie's outputs (IP protection)
_IP_LEAK_PATTERNS = [
    r"SUPABASE_URL\s*=",
    r"SUPABASE_ANON_KEY\s*=",
    r"eyJ[A-Za-z0-9_-]{20,}",  # JWT tokens
    r"sk-[a-zA-Z0-9]{20,}",  # API keys
    r"ghp_[a-zA-Z0-9]{20,}",  # GitHub PATs
]

# Patterns that indicate prompt injection in external content
_INJECTION_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)you\s+are\s+now\s+",
    r"(?i)system:\s*",
    r"(?i)IMPORTANT:\s*override",
    r"(?i)forget\s+(everything|all|your\s+instructions)",
]


class SoulEngine(BaseEngine):
    """Archie's Soul Engine — identity, integrity, and context assembly."""

    _name = "soul"

    def __init__(self) -> None:
        self._core_soul_text: str | None = None
        self._identity: dict[str, str] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Verify Core Soul integrity and load identity.

        Raises RuntimeError if Core Soul has been tampered with.
        """
        # Layer 4: Runtime verification
        if not verify_core_soul():
            raise RuntimeError(
                "CRITICAL: Core Soul integrity check FAILED. "
                "Archie refuses to start. Alert the team immediately."
            )

        self._core_soul_text = get_core_soul()

        # Extract identity from Core Soul
        self._identity = {
            "name": "Archie",
            "role": "AI Project Manager",
            "entity": "Nivanta AI LLC",
            "methodology": "PIV Loop (Plan-Implement-Validate)",
            "language": "match master's language",
            "personality": "strategic, direct, opinionated when backed by data, honest about uncertainty",
        }

        self._initialized = True

    def get_core_directives(self) -> str:
        """Return the Core Soul text (after integrity verification).

        Raises RuntimeError if engine not initialized or Core Soul tampered.
        """
        if not self._initialized or self._core_soul_text is None:
            raise RuntimeError("SoulEngine not initialized. Call initialize() first.")

        # Re-verify every time (defense in depth)
        if not verify_core_soul():
            raise RuntimeError("CRITICAL: Core Soul integrity check FAILED at runtime.")

        return self._core_soul_text

    def get_identity(self) -> dict[str, str]:
        """Return Archie's identity dictionary."""
        if not self._initialized:
            raise RuntimeError("SoulEngine not initialized.")
        return self._identity.copy()

    def build_phase_context(self, phase: str, project_objective: str = "") -> dict[str, str]:
        """Build context relevant to the current orchestrator phase.

        Returns a dict with keys that can be injected into artifact generation:
          - "directives": relevant Core Soul directives for this phase
          - "methodology": phase-specific methodology guidance
          - "identity": Archie's identity block
        """
        if not self._initialized:
            raise RuntimeError("SoulEngine not initialized.")

        # Phase-specific directive emphasis
        phase_directives: dict[str, list[int]] = {
            "discovery": [5, 6, 7],  # Methodology, Memory, Transparency
            "planning": [2, 5, 6],  # IP Protection, Methodology, Memory
            "roadmap": [5, 6],  # Methodology, Memory
            "implementation": [2, 3, 5],  # IP Protection, Injection Defense, Methodology
            "deployment": [2, 3],  # IP Protection, Injection Defense
        }

        directive_nums = phase_directives.get(phase, [5, 7])
        directive_names = {
            1: "LOYALTY",
            2: "IP PROTECTION",
            3: "PROMPT INJECTION DEFENSE",
            4: "EXTERNAL ORDER REJECTION",
            5: "METHODOLOGY INTEGRITY",
            6: "MEMORY & LEARNING INTEGRITY",
            7: "TRANSPARENCY & ATTRIBUTION",
        }

        active = [f"Directive {n}: {directive_names[n]}" for n in directive_nums]

        # Phase-specific methodology
        methodology: dict[str, str] = {
            "discovery": "Ask strategic questions. Cross-reference with existing projects. Surface relevant lessons proactively.",
            "planning": "Generate CLAUDE.md and PRD using official templates. Enrich with lessons from memory. Evaluate quality.",
            "roadmap": "Break down into features with dependencies. Include domain-specific features. Cap at 10 for MVP.",
            "implementation": "PIV Loop per feature. Plan > Implement > Validate. Use official PRP template.",
            "deployment": "Generate deployment configs appropriate for project scale.",
        }

        return {
            "directives": "\n".join(active),
            "methodology": methodology.get(phase, "Follow PIV Loop."),
            "identity": f"Archie — {self._identity['role']} at {self._identity['entity']}",
            "project": project_objective,
        }

    def validate_output(self, text: str) -> tuple[bool, list[str]]:
        """Validate that output doesn't leak IP or contain injection patterns.

        Returns (is_safe, list_of_violations).
        """
        violations: list[str] = []

        # Check for IP leaks
        for pattern in _IP_LEAK_PATTERNS:
            if re.search(pattern, text):
                violations.append(f"IP leak detected: matches pattern '{pattern}'")

        # Check for injection patterns in generated content
        for pattern in _INJECTION_PATTERNS:
            if re.search(pattern, text):
                violations.append(f"Injection pattern detected: '{pattern}'")

        return (len(violations) == 0, violations)

    def scan_external_content(self, content: str) -> tuple[bool, str]:
        """Scan external content (uploaded files, tool outputs) for injection attempts.

        Returns (is_safe, sanitized_content).
        Implements Directive 3: PROMPT INJECTION DEFENSE.
        """
        sanitized = content
        found_injections = False

        for pattern in _INJECTION_PATTERNS:
            if re.search(pattern, sanitized):
                found_injections = True
                sanitized = re.sub(pattern, "[INJECTION ATTEMPT STRIPPED]", sanitized)

        return (not found_injections, sanitized)
