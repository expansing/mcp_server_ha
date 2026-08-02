from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.modules.automations.action import EnableAutomationAction
from ha_mcp.modules.automations.analyzer import AutomationsAnalyzer
from ha_mcp.modules.automations.collector import AutomationsCollector


class AutomationsModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = AutomationsCollector(ha_provider)
        self._analyzer = AutomationsAnalyzer()
        self._action = EnableAutomationAction()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
