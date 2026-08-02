from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Collector
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository


class IntegrationGenericCollector:
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
            domain = entity_id.split(".")[0] if "." in entity_id else "unknown"
            observations.append(
                Observation(
                    id=f"integration-{domain}-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data={"domain": domain, "state": state.get("state"), "entity_id": entity_id},
                    source="ha",
                )
            )
        return observations
