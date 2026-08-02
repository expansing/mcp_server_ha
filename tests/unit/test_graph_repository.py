from __future__ import annotations

import pytest

from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.graph.graph_repository import GraphRepository


class MinimalGraphRepo:
    async def get_node(self, node_id: str) -> GraphNode | None:
        return None

    async def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        return []

    async def find(self, query: dict[str, object]) -> list[GraphNode]:
        return []

    async def search(self, text: str) -> list[GraphNode]:
        return []

    async def update(self, node: GraphNode) -> None:
        pass

    async def remove(self, node_id: str) -> None:
        pass


class TestGraphRepositoryProtocol:
    def test_minimal_impl_conforms(self):
        repo = MinimalGraphRepo()
        assert isinstance(repo, GraphRepository)

    def test_missing_method_breaks_compliance(self):
        class BrokenRepo:
            async def get_node(self, node_id: str) -> GraphNode | None:
                return None

        broken = BrokenRepo()
        assert not isinstance(broken, GraphRepository)
