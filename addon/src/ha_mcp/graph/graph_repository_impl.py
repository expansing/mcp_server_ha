from __future__ import annotations

import math
from collections import Counter
from typing import Any

import networkx as nx

from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.graph.graph_repository import GraphRepository


class KnowledgeGraph:
    def __init__(self) -> None:
        self._graph = nx.MultiDiGraph()
        self._documents: list[str] = []
        self._node_ids: list[str] = []
        self._idf: dict[str, float] = {}

    def add_node(self, node: GraphNode) -> None:
        if node.id in self._graph.nodes:
            self.remove(node.id)
        self._graph.add_node(
            node.id,
            resource_kind=node.resource_kind,
            integration_domain=node.integration_domain,
            attributes=node.attributes,
        )
        self._index_node(node)

    def _index_node(self, node: GraphNode) -> None:
        attrs = node.attributes or {}
        text = " ".join(str(v) for v in [node.id, str(node.integration_domain or ""), str(attrs)]).lower()
        words = text.split()
        self._documents.append(" ".join(words))
        self._node_ids.append(node.id)
        self._update_idf()

    def _update_idf(self) -> None:
        self._idf = {}
        total = len(self._documents)
        for doc in self._documents:
            for word in set(doc.split()):
                self._idf[word] = math.log((total + 1) / (1 + sum(1 for d in self._documents if word in d.split()))) + 1

    def _tfidf(self, query: str, doc: str) -> float:
        query_words = query.lower().split()
        doc_words = doc.split()
        if not doc_words:
            return 0.0
        tf = Counter(doc_words)
        score = 0.0
        for word in query_words:
            if word in tf:
                score += tf[word] / len(doc_words) * self._idf.get(word, 0.0)
        return score

    def add_node(self, node: GraphNode) -> None:
        self._graph.add_node(
            node.id,
            resource_kind=node.resource_kind,
            integration_domain=node.integration_domain,
            attributes=node.attributes,
        )

    def add_edge(self, source_id: str, target_id: str, relation: str = "depends_on") -> None:
        if source_id in self._graph.nodes and target_id in self._graph.nodes:
            self._graph.add_edge(source_id, target_id, relation=relation)

    def get_node(self, node_id: str) -> GraphNode | None:
        data = self._graph.nodes.get(node_id)
        if not data:
            return None
        return GraphNode(
            id=node_id,
            resource_kind=data.get("resource_kind", ResourceKind.ENTITY),
            integration_domain=data.get("integration_domain"),
            attributes=data.get("attributes", {}),
        )

    def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        if node_id not in self._graph.nodes:
            return []
        if direction == "out":
            neighbor_ids = list(self._graph.successors(node_id))
        elif direction == "in":
            neighbor_ids = list(self._graph.predecessors(node_id))
        else:
            neighbor_ids = list(self._graph.predecessors(node_id)) + list(self._graph.successors(node_id))
        return [self.get_node(nid) for nid in neighbor_ids if nid in self._graph.nodes]

    def find(self, query: dict[str, Any]) -> list[GraphNode]:
        results: list[GraphNode] = []
        for node_id, data in self._graph.nodes(data=True):
            match = True
            for key, value in query.items():
                if data.get(key) != value:
                    match = False
                    break
            if match:
                results.append(self.get_node(node_id))
        return results

    def search(self, text: str) -> list[GraphNode]:
        scored: list[tuple[float, GraphNode]] = []
        for idx, doc in enumerate(self._documents):
            score = self._tfidf(text, doc)
            if score > 0:
                node = self.get_node(self._node_ids[idx])
                if node:
                    scored.append((score, node))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [node for _, node in scored[:50]]

    def update(self, node: GraphNode) -> None:
        self.add_node(node)

    def remove(self, node_id: str) -> None:
        if node_id in self._graph.nodes:
            self._graph.remove_node(node_id)

    def get_all_nodes(self) -> list[GraphNode]:
        return [self.get_node(nid) for nid in self._graph.nodes]

    def get_all_edges(self) -> list[tuple[str, str, str]]:
        return [(u, v, d.get("relation", "depends_on")) for u, v, d in self._graph.edges(data=True)]


class GraphRepositoryImpl:
    def __init__(self) -> None:
        self._kg = KnowledgeGraph()

    async def get_node(self, node_id: str) -> GraphNode | None:
        return self._kg.get_node(node_id)

    async def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        return self._kg.neighbors(node_id, direction)

    async def find(self, query: dict[str, Any]) -> list[GraphNode]:
        return self._kg.find(query)

    async def search(self, text: str) -> list[GraphNode]:
        return self._kg.search(text)

    async def update(self, node: GraphNode) -> None:
        self._kg.update(node)

    async def remove(self, node_id: str) -> None:
        self._kg.remove(node_id)
