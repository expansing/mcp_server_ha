from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ha_mcp.models.graph_node import GraphNode


@runtime_checkable
class GraphRepository(Protocol):
    async def get_node(self, node_id: str) -> GraphNode | None:
        ...

    async def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        ...

    async def find(self, query: dict[str, Any]) -> list[GraphNode]:
        ...

    async def search(self, text: str) -> list[GraphNode]:
        ...

    async def update(self, node: GraphNode) -> None:
        ...

    async def remove(self, node_id: str) -> None:
        ...
