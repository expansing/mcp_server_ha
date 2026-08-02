from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class AutomationsCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            automations = await self._ha.get_automations()
        except Exception:
            automations = []
        for auto in automations:
            entity_id = auto.get("entity_id", "")
            observations.append(
                Observation(
                    id=f"automation-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data={
                        "alias": auto.get("alias"),
                        "trigger": auto.get("trigger", []),
                        "condition": auto.get("condition", []),
                        "action": auto.get("action", []),
                        "enabled": auto.get("enabled", True),
                    },
                    source="ha",
                )
            )
        return observations
