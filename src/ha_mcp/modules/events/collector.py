from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class EventsCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            events = await self._ha.get_events()
        except Exception:
            events = []
        for event in events:
            event_id = event.get("id", "")
            observations.append(
                Observation(
                    id=f"event-{event_id}",
                    type=ObservationType.EVENT,
                    subject_id=event_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data=event,
                    source="ha",
                )
            )
        return observations
