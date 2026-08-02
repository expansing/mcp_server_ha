# Domain Model (v2.2)

## Overview

This document defines the core data models for the Home Assistant MCP Server. These are the types that flow through the deterministic analysis pipeline: Provider → Collector → Analyzer → Finding → Recommendation → Action → StagedEdit → TransactionManager.

---

## GraphNode

```python
@dataclass(frozen=True)
class GraphNode:
    id: str                              # HA's unique_id (or entity_id as fallback)
    resource_kind: ResourceKind           # ENTITY, DEVICE, WORKFLOW, ...
    integration_domain: str | None = None # e.g., "tesla", "mqtt", "homeassistant"
    attributes: dict[str, Any] = field(default_factory=dict)
```

**Key points**:
- `id` reuses HA's own `unique_id` (or `entity_id` for entities without unique_id) — no invented UUID scheme
- `integration_domain` comes from HA's config entry / device registry — enables generic queries across any integration
- `attributes` holds whatever the provider finds useful (raw HA attributes, config, state, etc.)
- No `relationships` field — relationships are managed by the graph repository, not stored on nodes

---

## ResourceKind (Flat Enum)

```
ResourceKind:
  ENTITY          # sensor.temperature, binary_sensor.motion, input_*, counter, timer
  DEVICE          # device_tracker, person, zone
  WORKFLOW        # automation.morning, script.notify
  VISUALIZATION   # dashboard.energy, view.living_room
  EXECUTION       # addon.mosquitto, container.ha-mqtt
  CONFIGURATION   # configuration.yaml, secrets.yaml, package files
  TEMPLATE        # Jinja2 templates in automations/scripts/dashboards
  INTEGRATION     # integration.tesla, integration.mqtt
  SERVICE         # service calls, service definitions
```

**No inheritance, no abstract base class, no versioning.** Just a string tag on each GraphNode.

---

## Observation

```python
@dataclass(frozen=True)
class Observation:
    id: str
    type: ObservationType   # STATE, LOG, METRIC, TRACE, HISTORY, EVENT
    subject_id: str          # GraphNode.id (single subject — not a list)
    timestamp: datetime
    data: dict[str, Any]     # Type-specific payload
    source: str              # Provider name, e.g. "ha", "docker", "logs"

class ObservationType(Enum):
    STATE = "state"
    LOG = "log"
    METRIC = "metric"
    TRACE = "trace"
    HISTORY = "history"
    EVENT = "event"
```

**Key points**:
- Single `subject_id` — the GraphNode this observation is about
- `data` is a dict holding type-specific payload (no separate payload classes per type)
- `source` identifies which Provider produced it
- Unifies logs, metrics, traces, history, and events into one type

---

## Finding (Immutable)

```python
@dataclass(frozen=True)
class Finding:
    id: str
    subject_id: str              # GraphNode.id this finding is about
    category: str                # doubles as the "rule id" for explainability
    message: str
    severity: Severity
    evidence: tuple[str, ...] = ()   # Observation IDs, not free text
    confidence: float = 1.0
    schema_version: str = "1.0"  # lets external plugins declare compatibility
    metadata: dict[str, Any] = field(default_factory=dict)

class Severity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
```

**Key points**:
- `frozen=True` — immutable once produced by an Analyzer
- `evidence` holds real Observation IDs, not free text
- `category` acts as the rule identifier
- `subject_id` plus graph traversal answers "which nodes were involved"

---

## Recommendation (Immutable)

```python
@dataclass(frozen=True)
class Recommendation:
    id: str
    finding_ids: tuple[str, ...]
    action: str
    rationale: str
    effort: Effort
    risk: Risk
    priority: Literal["high", "medium", "low"]
    automatable: bool

class Effort(Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"

class Risk(Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
```

---

## Action (ABC)

```python
class Action(ABC):
    """Compiles Recommendations into StagedEdits — never mutates directly."""
    @abstractmethod
    async def compile(self, recommendation: Recommendation, context: dict) -> list[StagedEdit]:
        pass
```

---

## StagedEdit

```python
@dataclass(frozen=True)
class StagedEdit:
    id: str
    type: EditType
    target: str
    content: Any
    diff: str
    metadata: dict[str, Any] = field(default_factory=dict)

class EditType(Enum):
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    ENTITY_UPDATE = "entity_update"
    SERVICE_CALL = "service_call"
```

---

## ToolResult

```python
@dataclass
class ToolResult:
    status: Literal["success", "warning", "error", "info"]
    summary: str
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    transaction_id: str | None = None
```

---

## Intent (Internal Only)

```python
class Intent(Enum):
    INSPECT = "inspect"
    VALIDATE = "validate"
    DIAGNOSE = "diagnose"
    EXPLAIN = "explain"
    OPTIMIZE = "optimize"
    REPAIR = "repair"
    SIMULATE = "simulate"
```

**Key principle**: Intent is an internal dispatch convention only. It is never exposed as the MCP interface itself. The MCP tool surface stays as `diagnose_dashboard()`, `repair_dashboard()`, etc.

---

## Provider (Protocol)

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

**Key principle**: A provider implements whichever subset is meaningful for it. Git doesn't `subscribe()`; that's fine. `Provider.capabilities` (a `frozenset[Capability]`) replaces `hasattr` introspection.

---

## DetectionManifest

```python
@dataclass(frozen=True)
class DetectionManifest:
    ha_integrations: list[str] = field(default_factory=list)
    entities_pattern: list[str] = field(default_factory=list)
    addons: list[str] = field(default_factory=list)
    filesystem_paths: list[str] = field(default_factory=list)
    docker_containers: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    target_domains: list[str] = field(default_factory=list)
    required_providers: list[str] = field(default_factory=list)
    detection: DetectionManifest
```

---

## Analysis Pipeline Protocols

```python
class Collector(Protocol):
    async def collect(self, graph: GraphRepository) -> list[Observation]: ...

class Analyzer(Protocol):
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]: ...
```

**Scope**: The pipeline applies to modules that inspect state and can propose changes (entities, automations, dashboards, `docker_health`, `integration_generic`). It does **not** apply to `search` or `context`, which are read-only query facilities with nothing to recommend.

---

## Transaction

```python
class TransactionStatus(Enum):
    OPEN = "open"
    VALIDATING = "validating"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"

@dataclass
class Transaction:
    id: str
    description: str
    status: TransactionStatus
    edits: list[StagedEdit] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)
    created_at: datetime
    requested_by: str = ""
    tool_name: str = ""
    committed_at: datetime | None = None
```

---

*These models form the **contract** between all layers. Keep them stable, versioned, and well-tested.*
