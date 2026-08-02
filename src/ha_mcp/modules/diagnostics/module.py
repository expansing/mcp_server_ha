from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.modules.diagnostics.analyzer import DiagnosticsAnalyzer
from ha_mcp.modules.diagnostics.collector import DiagnosticsCollector


class DiagnosticsModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = DiagnosticsCollector(ha_provider)
        self._analyzer = DiagnosticsAnalyzer()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
