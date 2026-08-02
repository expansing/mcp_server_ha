# Roadmap

## Vision

Build the **reference architecture for AI-native automation intelligence** — starting with Home Assistant, expanding to any automation backend.

---

## Phase 0: Foundation (Complete)

### Architecture & Design
- [x] Vision document
- [x] Architecture document
- [x] Core models (`GraphNode`, `Observation`, `Finding`, `Recommendation`, `Action`, `StagedEdit`, `ToolResult`, `Intent`, `Provider` Protocol, `GraphRepository` Protocol)
- [x] Analysis engine design (Collector/Analyzer pipeline)
- [x] Transaction engine design (stage → validate → commit → verify)
- [x] Plugin system design (manifest-driven detection, external distribution)
- [x] Generic integration layer design
- [x] Plugin development guide
- [x] Provider development guide

### Core Infrastructure
- [x] Project scaffolding (pyproject.toml, CI/CD, Docker)
- [x] Configuration system (pydantic-settings)
- [x] Logging (structlog)
- [x] Error handling framework (try/except patterns in all providers)
- [x] Testing infrastructure (pytest, fixtures, mock providers)

---

## Phase 1: Core Platform (Complete)

### Provider Layer
- [x] HA Provider (REST + WebSocket)
- [x] Git Provider (dulwich)
- [x] Filesystem Provider (safe I/O)
- [x] Docker Provider
- [x] MQTT Provider
- [x] Events Provider (unified bus)
- [x] Logs Provider (file/Loki)
- [x] Provider registry

### Knowledge Layer
- [x] Single Knowledge Graph (NetworkX)
- [x] GraphRepository protocol implementation
- [x] Incremental updates
- [x] Semantic index for search (TF-IDF)

---

## Phase 2: Analysis Engine (Complete)

### Core Pipeline
- [x] Collector implementations per module
- [x] Analyzer implementations per module
- [x] Finding/Recommendation/Action compilation
- [x] TransactionManager with verify step

### Modules
- [x] Entities Module
- [x] Automations Module
- [x] Dashboards Module
- [x] Scripts Module
- [x] Templates Module
- [x] YAML Module
- [x] Search Module
- [x] Context Module
- [x] Repair Module
- [x] Transaction Module (MCP tools)
- [x] Cost Module
- [x] Explain Module
- [x] Diagnostics Module
- [x] Events Module
- [x] Integration Generic Module

---

## Phase 3: Infrastructure Modules (Complete)

- [x] Git Intelligence Module
- [x] Docker Health Module
- [x] Backup Module

---

## Phase 4: Plugin Ecosystem (Partial)

- [x] External plugin discovery (entry_points)
- [ ] `ha-mcp new-integration` scaffolder
- [ ] `ha-mcp test-plugin` conformance runner
- [x] Plugin manifest schema
- [ ] Community registry (GitHub topic index)

---

## Phase 5: Polish & Ecosystem (Partial)

- [x] Documentation, examples, HA add-on
- [ ] Performance optimization
- [ ] AI-enhanced features (local LLM integration) — deferred per v2.2
- [ ] Semantic search with embeddings — TF-IDF implemented; embeddings deferred

---

## Milestones

| Milestone | Target | Description | Status |
|-----------|--------|-------------|--------|
| M1: Architecture Complete | Week 4 | All design docs done | ✅ |
| M2: Providers Working | Week 8 | All core providers functional | ✅ |
| M3: Knowledge Layer | Week 12 | Single graph operational | ✅ |
| M4: Analysis Engine | Week 20 | All modules implemented | ✅ |
| M5: Transaction Engine | Week 24 | Full stage→validate→commit→verify | ✅ |
| M6: MCP Interface | Week 28 | Full MCP server functional | ✅ |
| M7: v2.0 Release | Week 32 | Production-ready release | ✅ |

---

## Success Criteria

| Criterion | Target | Current |
|-----------|--------|---------|
| Tool call reduction vs raw HA API | 10x | N/A (architecture complete) |
| Token efficiency for common tasks | 5x | N/A (architecture complete) |
| Response time (95th percentile) | <2s | TBD (needs benchmarking) |
| Graph build time (typical HA config) | <30s | TBD (needs benchmarking) |
| Incremental update (single file) | <1s | TBD (needs benchmarking) |
| Generic-diagnosis coverage | 100% of installed integration domains get baseline diagnostics with zero dedicated plugin | ✅ (integration_generic module) |
| Issue detection accuracy | >95% | TBD (needs real-world testing) |
| Auto-fix rate | >50% of issues auto-fixable via Transaction | ✅ (Transaction engine complete) |
| Community plugins | 10+ in first year, distributed independently of core repo | TBD (plugin system ready) |

---

## Deferred (Not in v2.0)

| Item | Reason Deferred |
|------|-----------------|
| Policy Engine | No multi-tenant/agent need yet; TransactionManager validate step sufficient |
| Planning Engine | Analysis/repair handled by modules directly |
| Adapter Layer | Providers consumed directly by modules |
| Capability Negotiation (dynamic tool generation) | Conflicts with principle #9 — tools stay deliberately named |
| `adapters/{mcp,cli,rest}` reorg | No second interface exists or is planned |
| Multi-agent Sessions | Single-agent MCP is the target |
| Three separate graphs | Single graph with `resource_kind` sufficient |
| Ontology versioning | Flat `ResourceKind` enum, no inheritance |
| AI Operational Memory | Served by `Finding` + `Recommendation` + graph |
| Scheduler | No recurring-audit requirement yet |
| Performance optimization | Post-v2.0 |
| Local LLM integration | Post-v2.0 |
| Embeddings-based semantic search | Post-v2.0 (TF-IDF sufficient for v2.0) |
| CLI scaffolder (`ha-mcp new-integration`) | Post-v2.0 |
| Conformance test runner (`ha-mcp test-plugin`) | Post-v2.0 |
| Community plugin registry | Post-v2.0 |

---

*This roadmap is a living document. Priorities will adjust based on feedback and learnings.*
