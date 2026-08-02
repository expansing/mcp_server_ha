from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class YAMLCollector:
    def __init__(self, filesystem_provider: Provider) -> None:
        self._fs = filesystem_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            content = await self._fs.read("configuration.yaml")
        except Exception:
            content = ""
        observations.append(
            Observation(
                id="yaml-configuration",
                type=ObservationType.STATE,
                subject_id="configuration.yaml",
                timestamp=__import__("datetime").datetime.now(),
                data={"content": content, "path": "configuration.yaml"},
                source="filesystem",
            )
        )
        return observations
