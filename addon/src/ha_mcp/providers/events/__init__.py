from __future__ import annotations

import asyncio
from collections.abc import Callable
from typing import Any

from ha_mcp.models.provider_protocol import Capability
from ha_mcp.models.provider_protocol import Provider as Provider


class EventsProvider:
    name = "events"
    capabilities = frozenset({Capability.STREAM})

    def __init__(self) -> None:
        self._buffer_size: int = 10000
        self._listeners: list[Callable] = []

    async def initialize(self, config: dict[str, Any]) -> None:
        self._buffer_size = config.get("buffer_size", 10000)

    async def shutdown(self) -> None:
        self._listeners.clear()

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> str:
        raise NotImplementedError("EventsProvider.read not implemented")

    async def write(self, resource_id: str, content: Any) -> None:
        raise NotImplementedError("EventsProvider.write not implemented")

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("EventsProvider.execute not implemented")

    async def subscribe(self, filter: dict[str, Any], callback: Callable) -> None:
        self._listeners.append(callback)

    async def _emit(self, event: dict[str, Any]) -> None:
        for callback in self._listeners:
            try:
                result = callback(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                pass
