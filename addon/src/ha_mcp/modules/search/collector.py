from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class SearchCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            states = await self._ha.get_states()
        except Exception:
            states = []
        for state in states:
            entity_id = state.get("entity_id", "")
            if not entity_id:
                continue
            observations.append(
                Observation(
                    id=f"search-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data={
                        "entity_id": entity_id,
                        "state": state.get("state"),
                        "attributes": state.get("attributes", {}),
                        "friendly_name": state.get("attributes", {}).get("friendly_name", entity_id),
                    },
                    source="ha",
                )
            )
        return observations
