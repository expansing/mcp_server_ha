from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class ScriptsCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            scripts = await self._ha.get_scripts()
        except Exception:
            scripts = []
        for script in scripts:
            script_id = script.get("entity_id", "")
            observations.append(
                Observation(
                    id=f"script-{script_id}",
                    type=ObservationType.STATE,
                    subject_id=script_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data=script,
                    source="ha",
                )
            )
        return observations
