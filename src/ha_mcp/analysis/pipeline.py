from __future__ import annotations

from typing import Protocol, runtime_checkable

from ha_mcp.models.finding import Finding
from ha_mcp.models.graph_node import GraphNode
from ha_mcp.models.observation import Observation
from ha_mcp.graph.graph_repository import GraphRepository


@runtime_checkable
class Collector(Protocol):
    async def collect(self, graph: GraphRepository) -> list[Observation]:
        ...


@runtime_checkable
class Analyzer(Protocol):
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        ...
