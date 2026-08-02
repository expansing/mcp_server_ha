from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta

import pytest
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.modules.yaml.analyzer import YAMLAnalyzer
from ha_mcp.modules.yaml.collector import YAMLCollector
from ha_mcp.modules.yaml.module import YAMLModule


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


class FakeFSProvider:
    name = "filesystem"
    capabilities = frozenset()

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def read(self, path: str) -> str:
        return ""

    async def write(self, path: str, content: str) -> None:
        pass

    async def exists(self, path: str) -> bool:
        return True

    async def list(self, path: str) -> list[str]:
        return []


class TestYAMLAnalyzer:
    @pytest.mark.asyncio
    async def test_detects_empty_yaml(self):
        analyzer = YAMLAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="yaml-configuration",
                type=ObservationType.STATE,
                subject_id="configuration.yaml",
                timestamp=datetime.now(),
                data={"content": "", "path": "configuration.yaml"},
                source="filesystem",
            )
        ]
        findings = await analyzer.analyze(obs, graph)
        assert len(findings) == 1
        assert findings[0].category == "empty_yaml"
        assert findings[0].severity == Severity.WARNING


class TestYAMLModule:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        provider = FakeFSProvider()
        module = YAMLModule(provider)
        graph = FakeGraphRepo()
        findings = await module.run(graph)
        assert len(findings) == 1
        assert findings[0].category == "empty_yaml"
