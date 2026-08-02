from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer, Collector
from ha_mcp.models.finding import Finding
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository

from ha_mcp.modules.automations.analyzer import AutomationsAnalyzer
from ha_mcp.modules.automations.collector import AutomationsCollector
from ha_mcp.modules.automations.action import EnableAutomationAction


class AutomationsModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = AutomationsCollector(ha_provider)
        self._analyzer = AutomationsAnalyzer()
        self._action = EnableAutomationAction()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
