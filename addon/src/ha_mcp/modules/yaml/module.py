from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.modules.yaml.action import FixYAMLAction
from ha_mcp.modules.yaml.analyzer import YAMLAnalyzer
from ha_mcp.modules.yaml.collector import YAMLCollector


class YAMLModule:
    def __init__(self, filesystem_provider: Provider) -> None:
        self._collector = YAMLCollector(filesystem_provider)
        self._analyzer = YAMLAnalyzer()
        self._action = FixYAMLAction()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
