"""
Base Engine — Abstract base class for all Archie engines.

All engines follow the same lifecycle:
  1. __init__() — set up instance (no I/O)
  2. initialize() — async startup (verify, connect, load)
  3. is_ready — check if engine is operational
  4. shutdown() — async cleanup
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseEngine(ABC):
    """Abstract base class for Archie's 4 engines."""

    _name: str = "base"
    _initialized: bool = False

    @abstractmethod
    async def initialize(self) -> None:
        """Start the engine. Called once at MCP server startup."""
        ...

    async def shutdown(self) -> None:
        """Stop the engine. Called at MCP server shutdown."""
        self._initialized = False

    @property
    def is_ready(self) -> bool:
        """Check if the engine has been initialized successfully."""
        return self._initialized

    def __repr__(self) -> str:
        status = "ready" if self._initialized else "not initialized"
        return f"<{self.__class__.__name__} ({status})>"
