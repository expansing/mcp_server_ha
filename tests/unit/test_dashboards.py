from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta

import pytest
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.modules.dashboards.analyzer import DashboardsAnalyzer
from ha_mcp.modules.dashboards.collector import DashboardsCollector
from ha_mcp.modules.dashboards.module import DashboardsModule


class FakeGraphRepo:
    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}

    async def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    async def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        return []

    async def find(self, query: dict[str, Any]) -> list[GraphNode]:
        return list(self._nodes.values())

    async def search(self, text: str) -> list[GraphNode]:
        return []

    async def update(self, node: GraphNode) -> None:
        self._nodes[node.id] = node

    async def remove(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)


class FakeHAProvider:
    name = "ha"
    capabilities = frozenset()

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def get_dashboards(self) -> list[dict[str, Any]]:
        return [
            {
                "id": "dashboard1",
                "title": "Living Room",
                "url_path": "living-room",
                "cards": [{"type": "glance", "entity": "sensor.temp"}],
                "views": [{"title": "Main", "cards": []}],
            },
            {
                "id": "dashboard2",
                "title": "Empty",
                "url_path": "empty",
                "cards": [],
                "views": [],
            },
        ]


class TestDashboardsAnalyzer:
    @pytest.mark.asyncio
    async def test_detects_no_views(self):
        analyzer = DashboardsAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="dashboard-dashboard2",
                type=ObservationType.STATE,
                subject_id="dashboard2",
                timestamp=datetime.now(),
                data={
                    "id": "dashboard2",
                    "title": "Empty",
                    "url_path": "empty",
                    "cards": [],
                    "views": [],
                },
                source="ha",
            )
        ]
        findings = await analyzer.analyze(obs, graph)
        assert len(findings) == 1
        assert findings[0].category == "no_views"
        assert findings[0].severity == Severity.WARNING

    @pytest.mark.asyncio
    async def test_detects_deprecated_cards(self):
        analyzer = DashboardsAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="dashboard-dashboard1",
                type=ObservationType.STATE,
                subject_id="dashboard1",
                timestamp=datetime.now(),
                data={
                    "id": "dashboard1",
                    "title": "Living Room",
                    "url_path": "living-room",
                    "cards": [{"type": "glance", "entity": "sensor.temp"}],
                    "views": [{"title": "Main", "cards": []}],
                },
                source="ha",
            )
        ]
        findings = await analyzer.analyze(obs, graph)
        assert len(findings) == 1
        assert findings[0].category == "deprecated_cards"
        assert findings[0].severity == Severity.WARNING


class TestDashboardsModule:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        provider = FakeHAProvider()
        module = DashboardsModule(provider)
        graph = FakeGraphRepo()
        findings = await module.run(graph)
        categories = {f.category for f in findings}
        assert "no_views" in categories
        assert "deprecated_cards" in categories
