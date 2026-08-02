from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Collector
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository


class TemplatesCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            templates = await self._ha.get_templates()
        except Exception:
            templates = []
        for template in templates:
            template_id = template.get("entity_id", "")
            observations.append(
                Observation(
                    id=f"template-{template_id}",
                    type=ObservationType.STATE,
                    subject_id=template_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data={
                        "entity_id": template_id,
                        "content": template.get("content", ""),
                    },
                    source="ha",
                )
            )
        return observations
