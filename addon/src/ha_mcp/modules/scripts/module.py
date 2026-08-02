from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.modules.scripts.action import ScriptsAction
from ha_mcp.modules.scripts.analyzer import ScriptsAnalyzer
from ha_mcp.modules.scripts.collector import ScriptsCollector


class ScriptsModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = ScriptsCollector(ha_provider)
        self._analyzer = ScriptsAnalyzer()
        self._action = ScriptsAction()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
