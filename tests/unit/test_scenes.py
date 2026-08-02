from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta

import pytest
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.modules.scenes.analyzer import ScenesAnalyzer
from ha_mcp.modules.scenes.collector import ScenesCollector
from ha_mcp.modules.scenes.module import ScenesModule


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

    async def get_scenes(self) -> list[dict[str, Any]]:
        return [
            {
                "entity_id": "scene.morning",
                "name": "Morning",
                "entities": {"light.bedroom": {"state": "on"}},
            },
            {
                "entity_id": "scene.empty",
                "name": "Empty",
                "entities": {},
            },
        ]


class TestScenesAnalyzer:
    @pytest.mark.asyncio
    async def test_detects_empty_scene(self):
        analyzer = ScenesAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="scene-scene.empty",
                type=ObservationType.STATE,
                subject_id="scene.empty",
                timestamp=datetime.now(),
                data={
                    "entity_id": "scene.empty",
                    "name": "Empty",
                    "entities": {},
                },
                source="ha",
            )
        ]
        findings = await analyzer.analyze(obs, graph)
        assert len(findings) == 1
        assert findings[0].category == "empty_scene"
        assert findings[0].severity == Severity.INFO


class TestScenesModule:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        provider = FakeHAProvider()
        module = ScenesModule(provider)
        graph = FakeGraphRepo()
        findings = await module.run(graph)
        assert len(findings) == 1
        assert findings[0].category == "empty_scene"
