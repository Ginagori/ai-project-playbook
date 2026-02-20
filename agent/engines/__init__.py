"""
Archie's 4-Engine Architecture.

Engines:
  - SoulEngine: Core Soul integrity + context assembly
  - MemoryEngine: Unified knowledge retrieval + learned preferences
  - RouterEngine: Intent detection + agent dispatch + output sandbox
  - HeartbeatEngine: Proactive project health monitoring

The EngineCoordinator initializes all engines and provides a single
entry point for the MCP server.
"""

from __future__ import annotations

from agent.engines.base import BaseEngine
from agent.engines.heartbeat_engine import HeartbeatEngine
from agent.engines.memory_engine import MemoryEngine
from agent.engines.router_engine import RouterEngine
from agent.engines.soul_engine import SoulEngine


class EngineCoordinator:
    """Coordinates Archie's 4 engines — startup, lifecycle, access.

    Usage:
        coordinator = EngineCoordinator()
        await coordinator.initialize(supabase_client=db)

        # Access individual engines
        coordinator.soul.get_identity()
        coordinator.memory.search(...)
        coordinator.router.detect_intent(...)
        coordinator.heartbeat.get_dashboard()
    """

    def __init__(self) -> None:
        self.soul = SoulEngine()
        self.memory = MemoryEngine()
        self.router = RouterEngine()
        self.heartbeat = HeartbeatEngine()
        self._initialized = False

    async def initialize(
        self,
        supabase_client: object | None = None,
        sessions_store: dict | None = None,
    ) -> None:
        """Initialize all 4 engines in the correct order.

        Order matters:
          1. Soul Engine first (Core Soul verification — if this fails, nothing starts)
          2. Memory Engine (needs Supabase client)
          3. Router Engine (needs available agents)
          4. Heartbeat Engine (needs sessions store + Supabase)
        """
        # 1. Soul Engine — MUST succeed or Archie refuses to start
        await self.soul.initialize()

        # 2. Memory Engine
        self.memory = MemoryEngine(supabase_client)
        await self.memory.initialize()

        # 3. Router Engine
        await self.router.initialize()

        # 4. Heartbeat Engine
        await self.heartbeat.initialize(
            sessions_store=sessions_store,
            supabase_client=supabase_client,
        )

        self._initialized = True

    async def shutdown(self) -> None:
        """Shutdown all engines in reverse order."""
        await self.heartbeat.shutdown()
        await self.router.shutdown()
        await self.memory.shutdown()
        await self.soul.shutdown()
        self._initialized = False

    @property
    def is_ready(self) -> bool:
        """Check if all engines are initialized."""
        return (
            self._initialized
            and self.soul.is_ready
            and self.memory.is_ready
            and self.router.is_ready
            and self.heartbeat.is_ready
        )

    def status(self) -> dict[str, bool]:
        """Return status of each engine."""
        return {
            "soul": self.soul.is_ready,
            "memory": self.memory.is_ready,
            "router": self.router.is_ready,
            "heartbeat": self.heartbeat.is_ready,
            "all_ready": self.is_ready,
        }

    def __repr__(self) -> str:
        ready = sum(1 for v in self.status().values() if v) - 1  # subtract all_ready
        return f"<EngineCoordinator ({ready}/4 engines ready)>"


__all__ = [
    "BaseEngine",
    "SoulEngine",
    "MemoryEngine",
    "RouterEngine",
    "HeartbeatEngine",
    "EngineCoordinator",
]
