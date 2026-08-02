# Analysis Engine

## Overview

The Analysis Engine answers questions about the system by applying Collectors and Analyzers against the knowledge graph. It follows a deterministic pipeline with no LLM dependency in the core.

---

## Core Pipeline

```
Provider → Collector → Analyzer → Finding(s) → Recommendation(s) → Action(s) → StagedEdit(s) → TransactionManager → validate → commit → verify
```

- **Collector**: Pulls raw data from Providers (HA API, git, filesystem, etc.)
- **Analyzer**: Given Observations and graph context, produces Findings only (never modifies state)
- **Finding**: Immutable fact with evidence (Observation IDs), confidence, category (rule id)
- **Recommendation**: References Finding(s), proposes an Action
- **Action**: Compiles Recommendations into `StagedEdit`s — never mutates directly
- **TransactionManager**: Stages, validates, commits, verifies

**Scope**: The pipeline applies to modules that inspect state and can propose changes (entities, automations, dashboards, `docker_health`, `integration_generic`). It does **not** apply to `search` or `context`, which are read-only query facilities with nothing to recommend.

---

## Collector

```python
class Collector(Protocol):
    async def collect(self, graph: GraphRepository) -> list[Observation]: ...
```

A Collector pulls raw data from Providers and produces Observations. Each module implements its own Collectors for the data sources it needs.

---

## Analyzer

```python
class Analyzer(Protocol):
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]: ...
```

An Analyzer takes Observations and graph context, then produces Findings. It never modifies state — that's the Action's job.

---

## Finding → Recommendation → Action

A module's Analyze phase produces Findings. Its Repair/Optimize phase takes Findings, produces Recommendations, then compiles them into StagedEdits via Actions:

```python
# Inside a module (e.g., modules/dashboards/)
class DiagnoseDashboard(Collector, Analyzer):
    async def analyze(self, observations, graph):
        findings = []
        for card in observations:
            if card.data.get("deprecated"):
                findings.append(Finding(
                    id=generate_id(),
                    subject_id=card.subject_id,
                    category="dashboard.deprecated_card",
                    message=f"Card uses deprecated type {card.data['type']}",
                    severity=Severity.WARNING,
                    evidence=(card.id,),
                ))
        return findings

class RepairDashboard(Action):
    async def compile(self, recommendation, context):
        return [StagedEdit(
            id=generate_id(),
            type=EditType.FILE_WRITE,
            target=recommendation.target,
            content=new_content,
            diff=generate_diff(...),
        )]
```

---

## Key Design Constraints

| Constraint | Rationale |
|------------|-----------|
| No LLM in core | Deterministic tests, cheap CI, offline/REST/CLI usable |
| Analyzers never modify state | Single mutation path through TransactionManager |
| Findings are immutable | Re-analysis produces new Finding; never edit in place |
| Verify every commit | Re-run the check that produced the original Finding |
| Intent is internal only | MCP tool surface stays deliberately named, not assembled from introspection |

---

## Performance Considerations

| Concern | Solution |
|---------|----------|
| Graph query latency | Indexed lookups, query caching, batch queries |
| Observation volume | Time-partitioned, filtered per Collector |
| Analysis time | Incremental updates, rule indexing by resource kind |

---

*The analysis engine is deliberately simple: Collectors gather, Analyzers reason, Actions compile. No orchestration framework, no event bus, no planning engine — just the pipeline.*
