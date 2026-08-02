from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class DiagnosticsCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        states = await self._ha.get_states()
        for state in states:
            entity_id = state.get("entity_id", "")
            if not entity_id:
                continue
            last_changed = state.get("last_changed")
            try:
                timestamp = __import__("datetime").datetime.fromisoformat(last_changed) if last_changed else __import__("datetime").datetime.now()
            except (ValueError, TypeError):
                timestamp = __import__("datetime").datetime.now()
            observations.append(
                Observation(
                    id=f"state-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=timestamp,
                    data={
                        "state": state.get("state"),
                        "attributes": state.get("attributes", {}),
                        "last_changed": last_changed,
                        "last_updated": state.get("last_updated"),
                    },
                    source="ha",
                )
            )
        return observations
