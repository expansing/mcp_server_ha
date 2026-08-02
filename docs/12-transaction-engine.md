# Transaction Engine

## Overview

The Transaction Engine provides **atomic, consistent, isolated, durable (ACID)** operations for multi-resource changes. It integrates with Git for version control and supports rollback on failure.

---

## Transaction Model

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

## Transaction Manager

```python
class TransactionManager:
    def __init__(self, providers: ProviderRegistry, graph: GraphRepository):
        self.providers = providers
        self.graph = graph
        self.current: Transaction | None = None
    
    async def begin(self, description: str, tool_name: str = "", requested_by: str = "") -> Transaction: ...
    async def stage(self, edit: StagedEdit) -> None: ...
    async def validate(self) -> list[ValidationResult]: ...
    async def commit(self, message: str) -> CommitResult: ...
    async def verify(self, check: Callable[[], bool]) -> bool: ...
    async def rollback(self) -> None: ...
    def status(self) -> Transaction | None: ...
```

---

## Workflow

```
begin(description, tool_name, requested_by)
    │
    ▼
stage(edit) ──► (repeat for each edit)
    │
    ▼
validate() ──► returns ValidationResult list
    │
    ▼
commit(message) ──► applies edits atomically
    │
    ▼
verify(check) ──► re-runs original check to confirm resolution
    │
    ├── success ──► COMMITTED
    │
    └── failure ──► rollback() ──► ROLLED_BACK
```

**Key principle**: Verify is a required final step — every commit re-runs the check that produced the original Finding to confirm it's resolved.

---

## Git Integration

```python
class GitTransactionIntegration:
    async def create_worktree(self, branch: str) -> str: ...
    async def commit_worktree(self, branch: str, message: str) -> GitCommit: ...
    async def remove_worktree(self, branch: str, force: bool = False) -> None: ...
```

---

## Snapshots

```python
class Snapshot:
    type: SnapshotType
    target: str
    content: Any
    created_at: datetime

class SnapshotType(Enum):
    FILE = "file"
    RESOURCE = "resource"
```

---

*The Transaction Engine provides **safe, auditable, reversible** multi-resource operations with **Git integration** and **graph consistency guarantees**. Only the TransactionManager commits state; Actions never write directly.*
