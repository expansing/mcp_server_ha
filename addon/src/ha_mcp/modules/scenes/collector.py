from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class ScenesCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            scenes = await self._ha.get_scenes()
        except Exception:
            scenes = []
        for scene in scenes:
            entity_id = scene.get("entity_id", "")
            observations.append(
                Observation(
                    id=f"scene-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data={
                        "entity_id": entity_id,
                        "name": scene.get("name"),
                        "entities": scene.get("entities", {}),
                    },
                    source="ha",
                )
            )
        return observations
