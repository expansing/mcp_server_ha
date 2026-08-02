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
- [ ] Project scaffolding (pyproject.toml, CI/CD, Docker)
- [ ] Configuration system (pydantic-settings)
- [ ] Logging (structlog)
- [ ] Error handling framework
- [ ] Testing infrastructure (pytest, fixtures, mock providers)

---

## Phase 1: Core Platform

### Provider Layer
- [ ] HA Provider (REST + WebSocket)
- [ ] Git Provider (dulwich)
- [ ] Filesystem Provider (safe I/O)
- [ ] Docker Provider
- [ ] MQTT Provider
- [ ] Events Provider (unified bus)
- [ ] Logs Provider (file/Loki)
- [ ] Provider registry

### Knowledge Layer
- [ ] Single Knowledge Graph (NetworkX)
- [ ] GraphRepository protocol implementation
- [ ] Incremental updates
- [ ] Semantic index for search

---

## Phase 2: Analysis Engine

### Core Pipeline
- [ ] Collector implementations per module
- [ ] Analyzer implementations per module
- [ ] Finding/Recommendation/Action compilation
- [ ] TransactionManager with verify step

### Modules
- [ ] Entities Module
- [ ] Automations Module
- [ ] Dashboards Module
- [ ] Scripts Module
- [ ] Templates Module
- [ ] YAML Module
- [ ] Search Module
- [ ] Context Module
- [ ] Repair Module
- [ ] Transaction Module (MCP tools)
- [ ] Cost Module
- [ ] Explain Module
- [ ] Diagnostics Module
- [ ] Events Module
- [ ] Integration Generic Module

---

## Phase 3: Infrastructure Modules

- [ ] Git Intelligence Module
- [ ] Docker Health Module
- [ ] Backup Module

---

## Phase 4: Plugin Ecosystem

- [ ] External plugin discovery (local dirs + entry_points)
- [ ] `ha-mcp new-integration` scaffolder
- [ ] `ha-mcp test-plugin` conformance runner
- [ ] Plugin manifest schema
- [ ] Community registry (GitHub topic index)

---

## Phase 5: Polish & Ecosystem

- [ ] Documentation, examples, HA add-on
- [ ] Performance optimization
- [ ] AI-enhanced features (local LLM integration)
- [ ] Semantic search with embeddings

---

## Milestones

| Milestone | Target | Description |
|-----------|--------|-------------|
| M1: Architecture Complete | Week 4 | All design docs done |
| M2: Providers Working | Week 8 | All core providers functional |
| M3: Knowledge Layer | Week 12 | Single graph operational |
| M4: Analysis Engine | Week 20 | All modules implemented |
| M5: Transaction Engine | Week 24 | Full stage→validate→commit→verify |
| M6: MCP Interface | Week 28 | Full MCP server functional |
| M7: v2.0 Release | Week 32 | Production-ready release |

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Tool call reduction vs raw HA API | 10x |
| Token efficiency for common tasks | 5x |
| Response time (95th percentile) | <2s |
| Graph build time (typical HA config) | <30s |
| Incremental update (single file) | <1s |
| Generic-diagnosis coverage | 100% of installed integration domains get baseline diagnostics with zero dedicated plugin |
| Issue detection accuracy | >95% |
| Auto-fix rate | >50% of issues auto-fixable via Transaction |
| Community plugins | 10+ in first year, distributed independently of core repo |

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

---

*This roadmap is a living document. Priorities will adjust based on feedback and learnings.*
