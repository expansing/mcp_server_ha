# Plugin System

## Overview

Plugins provide **domain expertise** — they consume providers and the knowledge graph to implement analysis, repair, and diagnostics capabilities. The built-in domain expertise lives in `modules/`; optional, externally-distributed extensions live in `plugins/`.

---

## Plugin Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      PLUGIN REGISTRY                            │
│  (Discovery, manifest loading, initialization, lifecycle)      │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│     Modules      │ │ Integration      │ │ Infrastructure   │
│   (built-in)     │ │   Plugins        │ │   Plugins        │
│                  │ │   (optional)     │ │   (optional)     │
│ • entities       │ │                  │ │ • git_intel      │
│ • automations    │ │  <empty by       │ │ • docker_health  │
│ • dashboards     │ │  default —       │ │ • backup         │
│ • scripts        │ │  extension       │ │                  │
│ • templates      │ │  point only>     │ │                  │
│ • yaml           │ │                  │ │                  │
│ • search         │ │                  │ │                  │
│ • context        │ │                  │ │                  │
│ • repair         │ │                  │ │                  │
│ • transaction    │ │                  │ │                  │
│ • cost           │ │                  │ │                  │
│ • explain        │ │                  │ │                  │
│ • diagnostics    │ │                  │ │                  │
│ • events         │ │                  │ │                  │
│ • integration_   │ │                  │ │                  │
│   generic        │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## Module / Plugin Interface

```python
# plugins/base.py
class PluginBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...  # e.g., "entities", "integrations.tesla"
    
    @property
    @abstractmethod
    def version(self) -> str: ...
    
    @property
    @abstractmethod
    def description(self) -> str: ...
    
    @property
    @abstractmethod
    def required_providers(self) -> list[str]: ...  # e.g., ["ha", "git"]
    
    @abstractmethod
    async def initialize(self, config: dict[str, Any], providers: ProviderRegistry, graph: GraphRepository) -> None: ...
    
    @abstractmethod
    def get_tools(self) -> list[Tool]: ...
    
    @abstractmethod
    def get_resources(self) -> list[Resource]: ...
    
    @abstractmethod
    async def shutdown(self) -> None: ...
    
    async def on_config_change(self, changes: list[ConfigChange]) -> None: ...
```

**Key points**:
- No `required_adapters` (adapters don't exist; modules consume providers directly)
- No `target_ontology_version` (ontology versioning was deferred)
- No `get_intent_handlers()`, `get_rules()`, or `on_resource_change()` — the tool surface is deliberately named, not assembled from introspection
- No `PluginCapabilities` dataclass — capability negotiation for modules was deferred

---

## Plugin Registry

```python
class PluginRegistry:
    def __init__(self):
        self._plugins: dict[str, PluginBase] = {}
        self._providers: ProviderRegistry
        self._graph: GraphRepository
    
    async def load_plugins(self, config: dict[str, Any], providers: ProviderRegistry, graph: GraphRepository) -> None:
        # 1. Discover plugins (built-in + external dirs + entry_points)
        # 2. Filter by config (enabled/disabled)
        # 3. Capability detection via manifest (auto-enable based on detected integrations)
        # 4. Resolve provider dependencies
        # 5. Initialize in dependency order
        # 6. Register tools and resources with MCP server
    
    def get_all_tools(self) -> list[Tool]: ...
    def get_all_resources(self) -> list[Resource]: ...
```

---

## Capability Detection (Auto-Configuration)

Replaces hardcoded `DETECTION_RULES` with manifest-driven detection:

```python
# plugins/capability.py
class CapabilityDetector:
    """Detects installed integrations/add-ons and enables plugins whose
    manifest matches — reads manifests, no hardcoded per-integration rules."""

    async def detect(self, providers: ProviderRegistry, manifests: list[PluginManifest]) -> list[str]:
        enabled = []
        for manifest in manifests:
            if await self._matches(manifest.detection, providers):
                enabled.append(manifest.name)
        return enabled
```

```yaml
# plugins/integrations/<name>/manifest.yaml  (or bundled with an external package)
name: "integrations.<name>"
version: "1.0.0"
description: "Specialized diagnostics for <name>"
target_domains: ["<ha_integration_domain>"]
required_providers: ["ha"]
detection:
  ha_integrations: ["<ha_integration_domain>"]
  entities_pattern: ["sensor.<name>_*"]
  addons: []
  filesystem_paths: []
  docker_containers: []
```

Core ships with **zero** integration manifests by default — `plugins/integrations/` is an empty, documented extension point. Any domain without a matching manifest still gets full baseline coverage via `integration_generic`.

---

## Core Module Specifications

### 1. Entities Module (`modules/entities/`)

**Tools**: `find_unused_entities()`, `find_missing_entities()`, `analyze_entity_health(entity_id)`, `get_entity_dependencies(entity_id)`, `show_dependency_graph(entity_id)`, `bulk_entity_operation(operation, filter)`, `find_stale_entities(threshold_days)`, `find_orphaned_helpers()`

### 2. Automations Module (`modules/automations/`)

**Tools**: `analyze_automation(automation_id)`, `explain_automation(automation_id)`, `find_broken_automations()`, `validate_automation_yaml(yaml_content)`, `get_automation_traces(automation_id, limit)`, `suggest_automation_improvements(automation_id)`, `simulate_automation(...)`, `find_duplicate_automations()`, `find_dead_code_automations()`, `show_dependency_graph(automation_id)`

### 3. Dashboards Module (`modules/dashboards/`)

**Tools**: `diagnose_dashboard(dashboard_name_or_id)`, `find_broken_dashboards()`, `validate_dashboard_yaml(yaml_content)`, `find_deprecated_cards()`, `analyze_dashboard_performance(dashboard_id)`, `suggest_dashboard_improvements(dashboard_id)`, `simulate_dashboard(dashboard_id, entity_states)`, `show_dependency_graph(dashboard_id)`

### 4. Scripts Module (`modules/scripts/`)

**Tools**: `analyze_script(script_id)`, `debug_script(script_id, inputs)`, `find_broken_scripts()`, `simulate_script(script_id, inputs, entity_states)`, `show_dependency_graph(script_id)`

### 5. Templates Module (`modules/templates/`)

**Tools**: `validate_template(template_string, context)`, `debug_template(template_string, context)`, `find_template_issues()`, `explain_template(template_string)`, `find_slow_templates(threshold_ms)`, `find_unsafe_templates()`

### 6. YAML Module (`modules/yaml/`)

**Tools**: `validate_yaml(file_path_or_content)`, `find_yaml_issues()`, `migrate_yaml(file_path, from_version, to_version)`, `format_yaml(file_path)`, `find_schema_violations()`

### 7. Search Module (`modules/search/`) ⭐⭐⭐⭐⭐

**Tools**: `search_configuration(query, type="all")`, `search_by_entity(entity_id)`, `search_by_pattern(pattern, file_type)`, `find_similar(name, type)`

### 8. Context Module (`modules/context/`) ⭐⭐⭐⭐⭐

**Tools**: `build_context(problem, scope="auto")`, `get_recent_context(hours)`

### 9. Repair Module (`modules/repair/`) ⭐⭐⭐⭐⭐

**Tools**: `repair_system()`, `repair_dashboard(dashboard_id)`, `repair_automation(automation_id)`, `repair_template(template_ref)`, `generate_fix_plan(issues)`

### 10. Transaction Module (`modules/transaction/`) ⭐⭐⭐⭐⭐

**Tools**: `transaction_begin(description)`, `transaction_stage(edit)`, `transaction_diff()`, `transaction_validate()`, `transaction_commit(message)`, `transaction_verify()`, `transaction_rollback()`, `transaction_status()`

### 11. Cost Module (`modules/cost/`) ⭐⭐⭐⭐⭐

**Tools**: `analyze_template_costs()`, `analyze_dashboard_costs()`, `analyze_automation_costs()`, `analyze_recorder_growth()`, `analyze_integration_costs()`, `get_resource_report()`

### 12. Explain Module (`modules/explain/`) ⭐⭐⭐⭐⭐

**Tools**: `explain_automation_failure(automation_id, trace_id)`, `explain_dashboard(dashboard_id)`, `explain_template(template_ref)`, `explain_script(script_id)`, `explain_entity(entity_id)`, `explain_integration(integration_domain)`

### 13. Diagnostics Module (`modules/diagnostics/`)

**Tools**: `full_system_diagnosis()`, `diagnose_integration(integration_domain)`, `find_configuration_drift()`, `health_score()`

### 14. Events Module (`modules/events/`) ⭐⭐⭐⭐⭐

**MCP Resources (live streams)**: `ha://events/state_changes`, `ha://events/automation_executions`, `ha://events/logs`, `ha://events/mqtt`, `ha://events/docker`

**Tools**: `subscribe_events(filter, duration)`, `replay_events(filter, since)`

### 15. Integration Generic Module (`modules/integration_generic/`) ⭐

Runs for **every** config entry / integration domain HA exposes, with no per-integration code:

**Tools**:
- `list_integrations()` — All installed integrations with domain, config entry state, entity count
- `diagnose_integration(domain)` — Generic health check for any domain
- `find_unhealthy_integrations()` — All domains with setup errors, retry loops, or entity availability below a threshold
- `check_integration_updates()` — Version comparison for HACS-managed and core integrations
- `show_dependency_graph(domain)` — Entities → automations → dashboards → scripts for a domain

**Internal capabilities**:
- Reads HA's config entry, device, and entity registries — no integration-specific parsing
- Correlates logs by logger name pattern (`homeassistant.components.<domain>`)
- Works identically whether the integration is core, HACS-installed, or a custom_component

---

## Integration Plugin Interface (Extension Point)

When a domain genuinely needs specialized reasoning, it can be implemented as a standalone plugin conforming to the same `PluginBase` interface:

```python
class IntegrationPlugin(PluginBase):
    """Optional, pluggable domain expertise for a specific integration.
    Not required — modules/integration_generic covers baseline diagnostics
    for any domain that doesn't have one of these."""

    @property
    @abstractmethod
    def target_domains(self) -> list[str]: ...

    @property
    @abstractmethod
    def detection_manifest(self) -> DetectionManifest: ...
```

Because it's just a `PluginBase` with a manifest, there's no structural difference between "core", "infrastructure", and "integration" plugins — the distinction is purely about where they're distributed from.

---

## Distribution Model — Plugins Don't Have to Live in This Repo

```yaml
plugins:
  auto_detect: true
  external_plugin_dirs:
    - "/config/ha_mcp_plugins"        # local, user-authored plugins
  external_packages:
    - "ha-mcp-plugin-community-xyz"   # installable via pip, discovered via entry_points
  enabled: []
  disabled: []
```

- **Local plugins**: drop a folder with `manifest.yaml` + implementation into `external_plugin_dirs`; picked up on next graph rebuild, no server code change.
- **Packaged plugins**: any pip-installable package registering a `ha_mcp.plugins` entry point is auto-discovered.
- **Community registry**: plugin discovery via a GitHub-topic-based index (`ha-mcp-plugin`), same as HACS's own model.

---

## External Plugin Development

### Plugin Package Structure

```
my-plugin/
├── pyproject.toml
├── src/
│   └── my_plugin/
│       ├── __init__.py
│       ├── plugin.py          # PluginBase implementation
│       ├── collectors/        # Data collection
│       ├── analyzers/         # Finding production
│       └── actions/           # StagedEdit compilation
├── tests/
└── README.md
```

### Entry Point

```toml
[project.entry-points."ha_mcp.plugins"]
my_plugin = "my_plugin.plugin:MyPlugin"
```

### Installation

```bash
pip install ha-mcp-my-plugin
# Platform auto-discovers via entry points
```

### Plugin Manifest

```python
# plugin.py
from ha_mcp.plugins import PluginBase, DetectionManifest

class MyPlugin(PluginBase):
    name = "custom.my_plugin"
    version = "1.0.0"
    description = "Custom analysis for MySystem"
    required_providers = ["ha"]
    
    @property
    def detection_manifest(self) -> DetectionManifest:
        return DetectionManifest(
            ha_integrations=["my_system"],
            entities_pattern=["sensor.my_system_*"]
        )
    
    async def initialize(self, config, providers, graph):
        self.ha = providers.get("ha")
        self.graph = graph
    
    def get_tools(self) -> list[Tool]: ...
    def get_resources(self) -> list[Resource]: ...
    async def shutdown(self) -> None: ...
```

---

## Plugin Lifecycle

```
DISCOVERED
    │
    ▼
VALIDATED (dependencies, manifest)
    │
    ▼
INITIALIZED (config, providers, graph)
    │
    ▼
ACTIVE (tools/resources registered with MCP)
    │
    ▼
SHUTDOWN (cleanup)
```

---

*Modules are the **domain expertise layer**. They know *what to look for* and *how to fix it* for their specific domain. External plugins extend them without modifying core.*
