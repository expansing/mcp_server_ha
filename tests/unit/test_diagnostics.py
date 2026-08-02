from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from ha_mcp.models.graph_node import GraphNode
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.modules.diagnostics.analyzer import DiagnosticsAnalyzer
from ha_mcp.modules.diagnostics.collector import DiagnosticsCollector
from ha_mcp.modules.diagnostics.module import DiagnosticsModule


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
                "entity_id": "sensor.ok",
                "state": "20",
                "attributes": {"unit_of_measurement": "°C"},
                "last_changed": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
            },
            {
                "entity_id": "sensor.bad",
                "state": "unavailable",
                "attributes": {},
                "last_changed": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
            },
        ]


class TestDiagnosticsAnalyzer:
    @pytest.mark.asyncio
    async def test_full_health_score(self):
        analyzer = DiagnosticsAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="state-sensor.ok",
                type=ObservationType.STATE,
                subject_id="sensor.ok",
                timestamp=datetime.now(tz=UTC),
                data={"state": "20", "attributes": {}, "last_changed": datetime.now(tz=UTC).isoformat(), "last_updated": datetime.now(tz=UTC).isoformat()},
                source="ha",
            ),
            Observation(
                id="state-sensor.bad",
                type=ObservationType.STATE,
                subject_id="sensor.bad",
                timestamp=datetime.now(tz=UTC),
                data={"state": "unavailable", "attributes": {}, "last_changed": datetime.now(tz=UTC).isoformat(), "last_updated": datetime.now(tz=UTC).isoformat()},
                source="ha",
            ),
        ]
        findings = await analyzer.analyze(obs, graph)
        assert len(findings) == 1
        assert findings[0].category == "health_score"
        assert findings[0].metadata["score"] == 50
        assert findings[0].metadata["total_entities"] == 2
        assert findings[0].metadata["critical"] == 1

    @pytest.mark.asyncio
    async def test_empty_observations(self):
        analyzer = DiagnosticsAnalyzer()
        graph = FakeGraphRepo()
        findings = await analyzer.analyze([], graph)
        assert findings == []


class TestDiagnosticsModule:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        provider = FakeHAProvider()
        module = DiagnosticsModule(provider)
        graph = FakeGraphRepo()
        findings = await module.run(graph)
        assert len(findings) == 1
        assert findings[0].category == "health_score"

    @pytest.mark.asyncio
    async def test_propagates_provider_error(self):
        class FailingHAProvider:
            async def get_states(self) -> list[dict[str, Any]]:
                raise RuntimeError("Home Assistant authentication failed")

        with pytest.raises(RuntimeError, match="authentication failed"):
            await DiagnosticsCollector(FailingHAProvider()).collect(FakeGraphRepo())
