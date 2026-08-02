from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Capability
from ha_mcp.models.provider_protocol import Provider as Provider


class LogsProvider:
    name = "logs"
    capabilities = frozenset({Capability.READ, Capability.STREAM})

    def __init__(self) -> None:
        self._source: str = "file"
        self._path: str = ""

    async def initialize(self, config: dict[str, Any]) -> None:
        self._source = config.get("source", "file")
        self._path = config.get("path", "/config/home-assistant.log")

    async def shutdown(self) -> None:
        pass

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> str:
        raise NotImplementedError("LogsProvider.read not implemented")

    async def write(self, resource_id: str, content: Any) -> None:
        raise NotImplementedError("LogsProvider.write not implemented")

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("LogsProvider.execute not implemented")

    async def subscribe(self, filter: dict[str, Any], callback: Any) -> None:
        raise NotImplementedError("LogsProvider.subscribe not implemented")

    async def query(self, filter: dict[str, Any]) -> list[Observation]:
        level = filter.get("level")
        results: list[Observation] = []
        try:
            with open(self._path, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if level and level not in line:
                        continue
                    results.append(
                        Observation(
                            id=f"log-{len(results)}",
                            type=ObservationType.LOG,
                            subject_id="",
                            timestamp=datetime.now(tz=UTC),
                            data={"message": line.rstrip(), "source": "logs"},
                            source="logs",
                        )
                    )
        except FileNotFoundError:
            pass
        return results

    async def tail(self, filter: dict[str, Any]) -> list[Observation]:
        return self.query(filter)
