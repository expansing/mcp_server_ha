from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Protocol, runtime_checkable

from ha_mcp.models.observation import Observation


class Capability(str, Enum):
    DISCOVER = "discover"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    STREAM = "stream"


@runtime_checkable
class Provider(Protocol):
    name: str
    capabilities: frozenset[Capability]

    async def initialize(self, config: dict[str, Any]) -> None:
        ...

    async def shutdown(self) -> None:
        ...

    async def discover(self) -> list[str]:
        ...

    async def read(self, resource_id: str) -> Observation:
        ...

    async def write(self, resource_id: str, content: Any) -> None:
        ...

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        ...

    async def subscribe(self, filter: dict[str, Any], callback: Callable) -> None:
        ...
