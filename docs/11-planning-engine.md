# Planning Engine — Deferred

## Status: Deferred (v2.1)

The Planning Engine was proposed in v1 as a separate layer for safe execution of changes. It was **explicitly deferred** in v2.1 review because:

- The analysis/repair split is handled by modules directly, not by a separate engine
- `Action.compile()` produces `StagedEdit`s which are handed to `TransactionManager` — this is the entire "planning" needed
- A full Plan → Validate → Approve → Execute → Verify → Rollback workflow is already embodied in the TransactionManager

**What we have instead**: 
- Modules produce `Finding`s and `Recommendation`s deterministically
- `Action.compile()` turns Recommendations into `StagedEdit`s
- `TransactionManager` handles stage → validate → commit → verify → rollback
- No separate Plan, PlanStep, ApprovalManager, or RollbackManager classes needed

**When to revisit**: If a second real agent or complex multi-step coordination requirement appears, the existing `Transaction` + `StagedEdit` types are sufficient to build plans on top without a dedicated engine.

---

*Deferred items are tracked in the design document's Review Decision Log (Round 1 and confirmed in every round since).*
