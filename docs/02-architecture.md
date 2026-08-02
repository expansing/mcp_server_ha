# Architecture: Home Assistant MCP Server

## Overview

This document describes the high-level architecture of the Home Assistant MCP Server. It defines the major layers, their responsibilities, and how they interact.

---

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTERFACES                                │
│  ┌─────────────┐                                                │
│  │    MCP      │                                                │
│  │  Interface  │                                                │
│  └──────┬──────┘                                                │
└─────────┼───────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MODULE / PLUGIN LAYER                       │
│  (Built-in modules + optional external plugins)                 │
│  Consumes Providers, produces Findings/Recommendations/Actions  │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼───────────────────┐
          ▼                  ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Analysis Engine │ │   Transaction    │ │   Event Stream   │
│                  │ │    Manager       │ │    Resources     │
│ │ Diagnose       │ │                  │ │                  │
│ │ Explain        │ │ Stage → Validate │ │ ha://events/*    │
│ │ Optimize       │ │ → Commit → Verify│ │                  │
│ │ Simulate       │ │ → Rollback       │ │                  │
│ │ Search         │ │                  │ │                  │
│ │ Cost analysis  │ │                  │ │                  │
│ └────────┬────────┘ └────────┬─────────┘ └──────────────────┘
│          │                    │
│          └────────────────────┼────────────────────┘
│                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      KNOWLEDGE LAYER                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           KNOWLEDGE GRAPH (Single)                       │   │
│  │  Nodes: GraphNode (resource_kind + integration_domain)   │   │
│  │  Edges: Relationships (TRIGGERS, READS, WRITES, etc.)    │   │
│  │  Index: Semantic index for natural language search       │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROVIDER LAYER                             │
│  ┌──────┐ ┌──────┐ ┌────────┐ ┌──────┐ ┌────────┐ ┌────────┐  │
│  │  HA  │ │ Git  │ │ Docker │ │ MQTT │ │ Logs   │ │ Events │  │
│  └──────┘ └──────┘ └────────┘ └──────┘ └────────┘ └────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer Responsibilities

### 1. Interface Layer
**Purpose**: Expose platform capabilities to external consumers.

| Interface | Protocol | Use Case |
|-----------|----------|----------|
| MCP | JSON-RPC 2.0 | AI assistants (Claude, Cursor, etc.) |

**Key Principle**: The interface is thin. It translates external requests → tool calls → Modules. The MCP tool surface stays deliberately named (`diagnose_dashboard()`, `repair_dashboard()`, etc.) — not assembled from introspection.

---

### 2. Module / Plugin Layer
**Purpose**: Domain expertise — analyze, diagnose, explain, optimize, repair.

**Modules** (built-in, always available):
- `entities`, `automations`, `dashboards`, `scripts`, `templates`, `yaml`
- `search`, `context`, `repair`, `transaction`, `cost`, `explain`, `diagnostics`, `events`
- `integration_generic` — baseline diagnostics for any integration domain
- `git_intel`, `docker_health`, `backup` (infrastructure)

**Plugins** (optional, externally distributed):
- Manifest-declared, discovered via local dir or entry_points
- Never required for baseline functionality

**Key Principle**: Modules consume Providers. They never reverse the dependency. A module implements whichever capabilities are meaningful for it (`INSPECT`, `VALIDATE`, `DIAGNOSE`, `EXPLAIN`, `OPTIMIZE`, `REPAIR`, `SIMULATE`) — these are an internal dispatch convention, not exposed through MCP.

---

### 3. Analysis Engine
**Purpose**: Answer questions about the system state through a deterministic pipeline.

**Single mutation path**:
```
Provider → Collector → Analyzer → Finding(s) → Recommendation(s) → Action(s) → StagedEdit(s) → TransactionManager → validate → commit → verify
```

- **Collector**: Pulls raw data from Providers
- **Analyzer**: Given Observations and graph context, produces Findings only (never modifies state)
- **Finding**: Immutable fact with evidence (Observation IDs), confidence, category (rule id)
- **Recommendation**: References Finding(s), proposes an Action
- **Action**: Compiles Recommendations into `StagedEdit`s — never mutates directly
- **TransactionManager**: Stages, validates, commits, verifies

**Key Principle**: No LLM dependency in the core. The pipeline produces deterministic results with zero AI model calls. An LLM may consume Findings and choose among Recommendations, or power an intentionally natural-language tool like `explain_template()` — but it sits outside the deterministic core.

---

### 4. Knowledge Layer (Single Graph)

#### Knowledge Graph
**Purpose**: Unified structural relationships, runtime state, and semantic meaning.

```
Automation ──triggers──► Entity
Automation ──calls──► Service
Dashboard ──contains──► Card ──references──► Entity
Script ──uses──► Template
Integration ──provides──► Entity
Entity ──state──► "unavailable"
Entity ──last_changed──► 2026-01-15T10:30:00Z
```

Every graph node carries an `integration_domain` attribute (from HA's config entry / device registry), so **any** query — dependency graphs, unused-entity detection, search — works identically regardless of which integration owns the entity. Nothing about the graph is integration-specific.

**Queries**: Dependencies, impact analysis, unused resources, blast radius, health, availability, staleness, anomalies, natural language search, concept exploration, cross-domain links

**Graph Repository** (Protocol):
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

### 5. Resource Layer (ResourceKind)

**Purpose**: Backend-agnostic domain model (flat enum, no inheritance).

```
ResourceKind:
  ENTITY          # sensor.temperature, binary_sensor.motion
  DEVICE          # device_tracker, person, zone
  WORKFLOW        # automation.morning, script.notify
  VISUALIZATION   # dashboard.energy, view.living_room
  EXECUTION       # addon.mosquitto, container.ha-mqtt
  CONFIGURATION   # configuration.yaml, secrets.yaml, package files
  TEMPLATE        # Jinja2 templates in automations/scripts/dashboards
  INTEGRATION     # integration.tesla, integration.mqtt
  SERVICE         # service calls, service definitions
```

**HA Mapping**:
| HA Concept | ResourceKind |
|------------|--------------|
| `sensor.temperature` | `ENTITY` |
| `binary_sensor.motion` | `ENTITY` |
| `device_tracker.phone` | `DEVICE` |
| `automation.morning` | `WORKFLOW` |
| `script.notify` | `WORKFLOW` |
| `dashboard.energy` | `VISUALIZATION` |
| `addon.mosquitto` | `EXECUTION` |
| `configuration.yaml` | `CONFIGURATION` |
| `template.battery` | `TEMPLATE` |
| `integration.tesla` | `INTEGRATION` |
| `service.light.turn_on` | `SERVICE` |

---

### 6. Provider Layer
**Purpose**: Low-level infrastructure access. Providers have **zero domain knowledge**. They only know how to talk to infrastructure.

**Provider** (Protocol, not ABC):
```python
class Capability(Enum):
    DISCOVER = "discover"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    STREAM = "stream"

class Provider(Protocol):
    name: str
    capabilities: frozenset[Capability]
    
    async def initialize(self, config: dict[str, Any]) -> None: ...
    async def shutdown(self) -> None: ...
    async def discover(self) -> list[str]: ...
    async def read(self, resource_id: str) -> Observation: ...
    async def write(self, resource_id: str, content: Any) -> None: ...
    async def execute(self, command: str, params: dict[str, Any]) -> Any: ...
    async def subscribe(self, filter: dict[str, Any], callback: Callable) -> None: ...
```

| Provider | Responsibility |
|----------|----------------|
| `HAProvider` | REST + WebSocket to Home Assistant |
| `GitProvider` | Repository operations (dulwich) |
| `FilesystemProvider` | Safe file I/O with sandboxing |
| `DockerProvider` | Container/image/network/volume ops |
| `MQTTProvider` | Broker connection, pub/sub |
| `LogsProvider` | File/Loki/syslog aggregation |
| `EventsProvider` | Unified event bus (HA WS, MQTT, Docker) |

**Key Principle**: A provider implements whichever subset of capabilities is meaningful for it. Git doesn't `subscribe()`; that's fine.

---

## Cross-Cutting Concerns

### Transaction System
All writes go through the TransactionManager:
```
Stage → Validate → Commit → Verify
```
- Snapshot-based rollback
- Git worktree integration
- Verification re-runs the check that produced the original Finding to confirm resolution
- `Transaction.requested_by` / `tool_name` for audit trails

### Generic Integration Layer
`integration_generic` module provides baseline diagnostics for **any** integration domain:
- Config entry state (loaded, setup_error, setup_retry, not_loaded)
- Entity availability breakdown
- Recent error/warning log lines correlated to the integration's logger namespace
- Automations/dashboards/scripts referencing this domain's entities (via knowledge graph)
- Works identically whether the integration is core, HACS-installed, or a custom_component

### Plugin System
- **Modules** (built-in): `entities`, `automations`, `dashboards`, `scripts`, `templates`, `yaml`, `search`, `context`, `repair`, `transaction`, `cost`, `explain`, `diagnostics`, `events`, `integration_generic`, `git_intel`, `docker_health`, `backup`
- **Plugins** (optional, external): local dir or installable package, manifest-declared, never required for baseline functionality
- Capability detection via manifest (not hardcoded rules)

---

*This architecture document defines the **structural foundation**. Domain model, analysis engine, and other components are detailed in separate documents.*
