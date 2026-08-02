from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.modules.templates.action import FixTemplateAction
from ha_mcp.modules.templates.analyzer import TemplatesAnalyzer
from ha_mcp.modules.templates.collector import TemplatesCollector


class TemplatesModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = TemplatesCollector(ha_provider)
        self._analyzer = TemplatesAnalyzer()
        self._action = FixTemplateAction()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
