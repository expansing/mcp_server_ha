from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Collector
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository


class DashboardsCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            dashboards = await self._ha.get_dashboards()
        except Exception:
            dashboards = []
        for dashboard in dashboards:
            dashboard_id = dashboard.get("id", "")
            observations.append(
                Observation(
                    id=f"dashboard-{dashboard_id}",
                    type=ObservationType.STATE,
                    subject_id=dashboard_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data={
                        "id": dashboard_id,
                        "title": dashboard.get("title"),
                        "url_path": dashboard.get("url_path"),
                        "cards": dashboard.get("cards", []),
                        "views": dashboard.get("views", []),
                    },
                    source="ha",
                )
            )
        return observations
