# Knowledge Graph

## Overview

The Knowledge Graph is a **single directed graph** used by all modules. Nodes are `GraphNode` instances carrying `resource_kind` and `integration_domain`; edges represent relationships between them.

---

## Graph Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE GRAPH (Single)                   │
│                                                                 │
│  Nodes: GraphNode (resource_kind + integration_domain)          │
│  Edges: Relationships (TRIGGERS, READS, WRITES, etc.)           │
│  Index: Semantic index for natural language search              │
│                                                                 │
│  Queries:                                                       │
│  • Dependencies, impact analysis, blast radius                  │
│  • Unused resources, orphaned resources                         │
│  • Health, availability, staleness                              │
│  • Anomalies, natural language search                           │
│  • Cross-domain links                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## GraphNode

```python
@dataclass(frozen=True)
class GraphNode:
    id: str
    resource_kind: ResourceKind
    integration_domain: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
```

Every node carries an `integration_domain` attribute (from HA's config entry / device registry), so **any** query works identically regardless of which integration owns the entity.

---

## Relationship Types

| Type | Source → Target | Example |
|------|-----------------|---------|
| `TRIGGERS` | WORKFLOW → ENTITY | Automation triggers on sensor |
| `READS` | WORKFLOW → ENTITY | Script reads sensor |
| `WRITES` | WORKFLOW → ENTITY | Automation sets input_boolean |
| `CALLS` | WORKFLOW → WORKFLOW | Script calls another script |
| `CONTAINS` | VISUALIZATION → COMPONENT | Dashboard contains card |
| `REFERENCES` | COMPONENT → ENTITY | Card references sensor |
| `USES` | WORKFLOW → TEMPLATE | Automation uses template |
| `PROVIDES` | INTEGRATION → ENTITY | Tesla integration provides sensor |
| `DEPENDS_ON` | EXECUTION → CONFIGURATION | Addon needs config file |
| `CONNECTS` | SERVICE → INTEGRATION | MQTT service connects HA |
| `DERIVED_FROM` | ENTITY → ENTITY | Template sensor from raw sensor |

---

## GraphRepository (Protocol)

```python
class GraphRepository(Protocol):
    async def get_node(self, node_id: str) -> GraphNode | None: ...
    async def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]: ...
    async def find(self, query: dict[str, Any]) -> list[GraphNode]: ...
    async def search(self, text: str) -> list[GraphNode]: ...
    async def update(self, node: GraphNode) -> None: ...
    async def remove(self, node_id: str) -> None: ...
```

---

## Query Patterns

### By Kind
```python
# All entities
nodes = graph.find({"resource_kind": ResourceKind.ENTITY})
```

### By Relationship
```python
# What automations use this entity?
dependents = graph.neighbors(entity_id, direction="in")
```

### By Integration Domain
```python
# All Tesla entities
tesla_nodes = graph.find({"integration_domain": "tesla"})
```

### Semantic Search
```python
# Natural language query
results = graph.search("battery level")
```

---

## Incremental Updates

```python
class IncrementalGraphUpdater:
    async def process_changes(self, changes: list[ConfigChange]) -> None:
        # Only re-parse affected files
        # Update affected nodes and edges
        # Update semantic index
        pass
```

---

## Storage

**Recommended**: NetworkX (in-memory) for development and typical configs. Kuzu or Neo4j for production large-configs.

---

*The single graph is the **single source of truth** for all analysis. It shields tools from backend changes and enables cross-tool consistency.*
