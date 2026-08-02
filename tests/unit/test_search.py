from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta

import pytest
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.modules.search.analyzer import SearchAnalyzer
from ha_mcp.modules.search.collector import SearchCollector
from ha_mcp.modules.search.module import SearchModule


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

    async def get_states(self) -> list[dict[str, Any]]:
        return [
            {
                "entity_id": "sensor.temperature",
                "state": "20",
                "attributes": {"friendly_name": "Temperature", "unit_of_measurement": "°C"},
                "last_changed": (datetime.now() - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now() - timedelta(hours=1)).isoformat(),
            },
            {
                "entity_id": "sensor.humidity",
                "state": "45",
                "attributes": {"friendly_name": "Humidity", "unit_of_measurement": "%"},
                "last_changed": (datetime.now() - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now() - timedelta(hours=1)).isoformat(),
            },
        ]


class TestSearchAnalyzer:
    @pytest.mark.asyncio
    async def test_matches_query(self):
        analyzer = SearchAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="search-sensor.temperature",
                type=ObservationType.STATE,
                subject_id="sensor.temperature",
                timestamp=datetime.now(),
                data={
                    "entity_id": "sensor.temperature",
                    "state": "20",
                    "attributes": {"friendly_name": "Temperature", "unit_of_measurement": "°C"},
                },
                source="ha",
            )
        ]
        findings = await analyzer.analyze(obs, graph, query="temperature")
        assert len(findings) == 1
        assert findings[0].category == "search_result"
        assert findings[0].metadata["count"] == 1

    @pytest.mark.asyncio
    async def test_no_match(self):
        analyzer = SearchAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="search-sensor.temperature",
                type=ObservationType.STATE,
                subject_id="sensor.temperature",
                timestamp=datetime.now(),
                data={
                    "entity_id": "sensor.temperature",
                    "state": "20",
                    "attributes": {"friendly_name": "Temperature"},
                },
                source="ha",
            )
        ]
        findings = await analyzer.analyze(obs, graph, query="nonexistent")
        assert findings == []


class TestSearchModule:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        provider = FakeHAProvider()
        module = SearchModule(provider)
        graph = FakeGraphRepo()
        findings = await module.run(graph, query="temperature")
        assert len(findings) == 1
        assert findings[0].metadata["count"] == 1
