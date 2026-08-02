# Vision: Home Assistant MCP Server

## Mission Statement

> **Build a developer-oriented Home Assistant MCP Server that serves as an "AI sysadmin" for Home Assistant.** Unlike existing MCP servers focused on home control (turn on lights, set thermostat), this server focuses on dashboard maintenance & diagnostics, automation analysis & troubleshooting, configuration validation, extensible integration diagnostics, Docker/add-on health monitoring, Git-aware configuration editing, and template development & debugging.

**Core Philosophy**: *Don't expose APIs, expose expertise.* The server is a **Home Assistant analysis platform that happens to expose an MCP interface**.

**Design Philosophy for Extensibility**: *Generic-first, specific-second.* Every integration installed in Home Assistant should get useful diagnostics automatically, with zero integration-specific code. A dedicated integration plugin is only justified when it adds real domain logic a generic analyzer can't infer (e.g., interpreting a charging schedule, decoding a camera's detection zones) — not merely to expose entities that are already visible generically.

---

## The Problem

Today's Home Assistant tools fall into two categories:

| Category | Examples | Limitation |
|----------|----------|------------|
| **Control Interfaces** | HA Dashboard, HomeKit | "Turn on the lights" — no understanding |
| **API Wrappers** | Existing MCP servers, REST clients | "Here are 200 endpoints, you figure it out" |

Neither helps an AI (or human) **understand** the system:
- Why did this automation fail?
- What entities are unused?
- Which dashboard cards are deprecated?
- What changed since last week that broke charging?
- How do I safely refactor this automation?

---

## The Solution: Home Assistant Analysis Platform

An **analysis platform** that happens to expose an MCP interface.

```
┌─────────────────────────────────────────────────────────────────┐
│                  HOME ASSISTANT ANALYSIS PLATFORM               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐                                              │
│   │   MCP        │                                              │
│   │   Interface  │                                              │
│   └──────┬───────┘                                              │
│          │                                                       │
│          ▼                                                       │
│  ┌─────────────────────┐                                        │
│  │  Module / Plugin    │  (built-in + optional external)        │
│  │  Layer              │                                        │
│  └──────────┬──────────┘                                        │
│             │                                                    │
│     ┌───────┼───────┐                                           │
│     ▼       ▼       ▼                                           │
│ ┌───────┐ ┌───────┐ ┌───────┐                                   │
│ │Analyze│ │Transact│ │Events │                                │
│ │Engine │ │Manager │ │Stream │                                │
│ └───┬───┘ └───┬───┘ └───┬───┘                                   │
│     │         │         │                                       │
│     └─────────┼─────────┘                                       │
│               ▼                                                 │
│  ┌─────────────────────┐                                        │
│  │   Knowledge Graph   │  (single graph,                        │
│  │   (Single)          │   resource_kind +                      │
│  │                     │   integration_domain)                  │
│  └──────────┬──────────┘                                        │
│             │                                                    │
│  ┌──────────┴──────────┐                                        │
│  │   Provider Layer    │  (HA, Git, FS, Docker,                 │
│  │                     │   MQTT, Logs, Events)                  │
│  └─────────────────────┘                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Principles

### 1. **Expose Expertise, Not APIs**
- Tools return *diagnoses*, not raw data
- `diagnose_dashboard("Energy")` not `get_dashboard_yaml()`

### 2. **High-Level Tools, Not API Wrappers**
- AI expresses *what it wants to achieve*
- Platform chooses *how* based on resource capabilities
- Intent is an internal dispatch convention only — never exposed as the MCP interface itself

### 3. **Single Mutation Path**
- All writes go through the TransactionManager (stage → validate → commit → verify)
- Nothing else is allowed to mutate state

### 4. **Findings Are Immutable**
- A `Finding` is a fact produced by an Analyzer at a point in time
- It is never edited in place — a re-analysis produces a new Finding

### 5. **Analyzers Never Modify State**
- Given Observations and graph context, an Analyzer produces Findings only
- Repair logic lives in Actions, not Analyzers

### 6. **Providers Never Contain Business Logic**
- A Provider is a thin transport (HA API, git, filesystem, Docker, MQTT)
- Domain knowledge belongs in Modules and Plugins that consume Providers, never the reverse

### 7. **Modules Consume Providers**
- Modules are the built-in domain-expertise units (entities, automations, dashboards, docker_health, integration_generic, etc.)

### 8. **Plugins Extend Modules**
- Plugins are optional, externally distributed (local dir or installable package), manifest-declared
- Never required for baseline functionality — `integration_generic` already covers any domain with no dedicated plugin

### 9. **Transactions Own All Writes**
- Actions compile Recommendations into `StagedEdit`s and hand them to the TransactionManager
- An Action never writes directly

### 10. **Verify Every Change**
- A commit isn't done until the specific check that produced the original Finding has been re-run and confirmed resolved

### 11. **Testability Over Abstraction**
- Prefer the version of a pattern that's easiest to unit test with mocked Providers over the version that's more "flexible"
- Abstractions are added when a concrete need appears in the first three modules — not speculatively

### 12. **No LLM Dependency in the Core**
- The pipeline (Provider → Collector → Analyzer → Finding → Recommendation) must be deterministic and runnable with zero AI model calls
- This keeps unit tests reproducible, CI cheap, and offline/non-MCP use possible
- An LLM may consume Findings and choose among Recommendations, or power an intentionally natural-language tool like `explain_template()` — but it sits outside the deterministic core, never inside it

### 13. **Explainability Is a Convention, Not a Subsystem**
- A Finding's `category` is its rule id; `evidence` holds real Observation IDs, not free text
- `subject_id` plus a graph traversal from it answers "which nodes were involved"
- Don't build a separate explanation subsystem — the existing fields already carry this if Analyzers populate them properly

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Tool call reduction vs raw API | 10x |
| Token efficiency for common tasks | 5x |
| Response time (95th percentile) | <2s |
| Graph build time (typical HA config) | <30s |
| Incremental update (single file) | <1s |
| Generic-diagnosis coverage | 100% of installed integration domains get baseline diagnostics with zero dedicated plugin |
| Issue detection accuracy | >95% |
| Auto-fix rate | >50% |
| Community plugins | 10+ in first year, distributed independently of core repo |

---

## Non-Goals

- ❌ Home control interface ("turn on lights")
- ❌ Replacement for HA UI
- ❌ General-purpose infrastructure monitoring
- ❌ Hardcoded HA version dependencies
- ❌ Multi-backend support (Node-RED, Docker, Kubernetes) — HA-only for v1.0
- ❌ Multi-agent orchestration — single-agent MCP is the target
- ❌ Policy Engine, Planning Engine, Adapter Layer — deferred until a concrete need appears

---

*This vision document defines **what** we're building and **why**. The architecture documents define **how**.*
