from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer, Collector
from ha_mcp.models.finding import Finding
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository

from ha_mcp.modules.search.analyzer import SearchAnalyzer
from ha_mcp.modules.search.collector import SearchCollector


class SearchModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = SearchCollector(ha_provider)
        self._analyzer = SearchAnalyzer()

    async def run(self, graph: GraphRepository, query: str = "") -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph, query=query)
        return findings
