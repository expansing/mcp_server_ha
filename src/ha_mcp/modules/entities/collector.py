from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class EntitiesCollector:
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
            node = GraphNode(
                id=entity_id,
                resource_kind=ResourceKind.ENTITY,
                integration_domain=entity_id.split(".")[0] if "." in entity_id else None,
                attributes={
                    "entity_id": entity_id,
                    "state": state.get("state"),
                },
            )
            try:
                await graph.update(node)
            except Exception:
                pass
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
