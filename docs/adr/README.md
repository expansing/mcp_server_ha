# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records for significant architectural decisions.

## ADR Format

Each ADR follows this format:

```
# ADR-NNN: Title

## Status
[Proposed | Accepted | Superseded | Deprecated]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing or have agreed to implement?

## Consequences
What becomes easier or more difficult to do because of this change?

### Positive
- ...

### Negative
- ...

### Neutral
- ...
```

## ADR Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| 001 | HA MCP Server scope | Accepted | 2026-01-15 |
| 002 | Single Knowledge Graph | Accepted | 2026-01-15 |
| 003 | Flat ResourceKind Enum | Accepted | 2026-01-15 |
| 004 | Provider/Module Separation | Accepted | 2026-01-15 |
| 005 | Intent (Internal Dispatch) | Accepted | 2026-01-15 |
| 006 | Transaction Engine with Git Integration | Accepted | 2026-01-15 |
| 007 | Policy Engine for Safety | Deferred | 2026-01-15 |
| 008 | Unified Observation Model | Accepted | 2026-01-15 |
| 009 | Plugin System with Manifest Detection | Accepted | 2026-01-15 |
| 010 | MCP as Primary Interface | Accepted | 2026-01-15 |

---

## ADR-001: HA MCP Server Scope

### Status
Accepted

### Context
The original design was for a generic "Automation Intelligence Platform" with multiple backends and interfaces. Through architectural review, it became clear this adds abstraction layers with no current implementation behind them.

### Decision
Keep the project scoped as a **Home Assistant MCP Server**:
- Single backend: Home Assistant
- Single interface: MCP
- Generic-first integration diagnostics via `integration_generic`
- External plugins for domain-specific extensions

### Consequences

#### Positive
- Focused implementation
- No speculative abstraction
- Faster time to working code

#### Negative
- Not reusable for other backends (not needed for v1.0)

---

## ADR-002: Single Knowledge Graph

### Status
Accepted

### Context
v1 proposed four specialized graphs (Topology, State, Semantic, Observation). Review showed this adds coordination complexity without solving a problem the first module (Entities) actually hits.

### Decision
Use a **single knowledge graph** with `GraphNode` nodes carrying `resource_kind` and `integration_domain`. Edges represent relationships. A semantic index is attached for search.

### Consequences

#### Positive
- Simpler incremental updates
- No cross-graph consistency concerns
- Single source of truth
- Faster to implement and test

#### Negative
- Single graph must handle all query patterns (solved by indexing)

---

## ADR-003: Flat ResourceKind Enum

### Status
Accepted

### Context
v1 proposed a full Resource class hierarchy with ontology versioning. Review showed this is speculative — there's exactly one backend (HA) and no plugin authors yet.

### Decision
Use a **flat `ResourceKind` enum** (`ENTITY`, `DEVICE`, `WORKFLOW`, `VISUALIZATION`, `EXECUTION`, `CONFIGURATION`, `TEMPLATE`, `INTEGRATION`, `SERVICE`) plus a single `GraphNode` dataclass. No inheritance, no ontology versioning.

### Consequences

#### Positive
- Simple, testable, no version migration burden
- HA-specific concepts map directly

#### Negative
- Less extensible if a second backend appears (deferred until then)

---

## ADR-004: Provider/Module Separation

### Status
Accepted

### Context
v1 proposed Providers → Adapters → Modules. Review showed Adapters add a layer with no current benefit — modules can consume providers directly.

### Decision
**Providers are consumed directly by modules.** No Adapter layer. Dependency direction is always Modules → Providers (never reverse).

### Consequences

#### Positive
- Simpler call chain
- Fewer abstractions to test
- Modules have full access to provider data

#### Negative
- Modules must know provider-specific details (acceptable — they're the domain expertise layer)

---

## ADR-005: Intent (Internal Dispatch)

### Status
Accepted

### Context
v1 proposed exposing Intent types through MCP. Review showed this conflicts with principle #9 (high-level tools, not API wrappers).

### Decision
`Intent` is an **internal-only** dispatch convention: `INSPECT`, `VALIDATE`, `DIAGNOSE`, `EXPLAIN`, `OPTIMIZE`, `REPAIR`, `SIMULATE`. It is never exposed as the MCP interface itself. The tool surface stays as `diagnose_dashboard()`, `repair_dashboard()`, etc.

### Consequences

#### Positive
- Clean MCP tool surface
- Internal refactoring freedom
- No capability-negotiation complexity exposed to AI

---

## ADR-006: Transaction Engine with Git Integration

### Status
Accepted

### Context
AI-driven changes need safety: atomicity, rollback, audit trail, verification.

### Decision
Transaction Engine with:
- Staging area for `StagedEdit`s
- Validation pipeline (simulation, lint, graph consistency)
- Git worktree per transaction (isolated changes)
- Snapshot-based rollback
- **Verify step**: re-run the original diagnosis after commit to confirm resolution
- `requested_by` / `tool_name` audit trails

### Consequences

#### Positive
- Safe AI-driven changes
- Full audit trail via Git
- Automatic rollback on verification failure

---

## ADR-007: Policy Engine for Safety

### Status
Deferred

### Context
v1 proposed a Policy Engine for declarative action constraints. Review showed the TransactionManager's validate step already provides essential safety guarantees, and no multi-tenant/compliance requirement exists yet.

### Decision
**Deferred.** The `TransactionManager.validate()` step runs simulation, lint, and graph-consistency checks. `require_approval` in config and audit trails cover immediate needs. Revisit if a second agent, multi-tenant deployment, or compliance requirement appears.

### Consequences

#### Positive
- Less speculative code
- TransactionManager sufficient for Phase 0–3

---

## ADR-008: Unified Observation Model

### Status
Accepted

### Context
Logs, metrics, traces, history, telemetry, and events were separate systems in v1. Hard to correlate across types.

### Decision
Single `Observation` dataclass with `ObservationType` enum (`STATE`, `LOG`, `METRIC`, `TRACE`, `HISTORY`, `EVENT`). `subject_id: str` links to a `GraphNode`. `data: dict[str, Any]` holds type-specific payload.

### Consequences

#### Positive
- Cross-type correlation via `subject_id`
- Single query interface
- No separate class hierarchy per observation type

---

## ADR-009: Plugin System with Manifest Detection

### Status
Accepted

### Context
v1 proposed hardcoded detection rules per integration. This touches core code for every new integration plugin.

### Decision
Manifest-driven capability detection:
- Each plugin ships a `DetectionManifest`
- `CapabilityDetector` reads manifests, no hardcoded rules
- Core ships with zero integration manifests — `plugins/integrations/` is empty by default
- `integration_generic` provides baseline diagnostics for any domain

### Consequences

#### Positive
- Adding a plugin never touches core code
- Community plugins distributed independently

---

## ADR-010: MCP as Primary Interface

### Status
Accepted

### Context
v1 proposed MCP as one interface among many (REST, Web UI, CLI). No second interface exists or is planned.

### Decision
MCP is the **primary and currently only** interface. The folder structure for hypothetical second interfaces (e.g., `adapters/{mcp,cli,rest}`) is not built until a second interface is actually being built.

### Consequences

#### Positive
- No speculative folder restructuring
- Single interface to test and maintain
