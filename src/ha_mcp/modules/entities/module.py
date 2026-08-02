from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.modules.entities.action import NotifyAction
from ha_mcp.modules.entities.analyzer import EntitiesAnalyzer
from ha_mcp.modules.entities.collector import EntitiesCollector


class EntitiesModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = EntitiesCollector(ha_provider)
        self._analyzer = EntitiesAnalyzer()
        self._action = NotifyAction()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
