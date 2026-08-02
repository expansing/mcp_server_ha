from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.modules.integration_generic.action import IntegrationGenericAction
from ha_mcp.modules.integration_generic.analyzer import IntegrationGenericAnalyzer
from ha_mcp.modules.integration_generic.collector import IntegrationGenericCollector


class IntegrationGenericModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = IntegrationGenericCollector(ha_provider)
        self._analyzer = IntegrationGenericAnalyzer()
        self._action = IntegrationGenericAction()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
