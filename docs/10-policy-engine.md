# Policy Engine — Deferred

## Status: Deferred (v2.1)

The Policy Engine was proposed in v1 as a declarative constraint system for actions. It was **explicitly deferred** in v2.1 review because:

- No second agent, second backend, or multi-tenant deployment exists yet
- The `TransactionManager` already provides the essential safety guarantees (stage → validate → commit → verify)
- `require_approval` in config and `Transaction.requested_by` / `tool_name` audit trails cover the immediate operational needs

**What we have instead**: The TransactionManager's validate step runs simulation, lint, and graph-consistency checks before any commit. The `verify` step re-runs the original diagnosis to confirm resolution. These are sufficient for Phase 0–3.

**When to revisit**: If a second real agent, a multi-tenant deployment, or a compliance requirement appears, a lightweight policy layer can be added without redesigning the core.

---

*Deferred items are tracked in the design document's Review Decision Log (Round 1 and confirmed in every round since).*
