# Plugin Development Guide

## Overview

This guide covers how to develop external plugins for the HA MCP Server. Plugins are optional, externally-distributed extensions that add domain expertise. They are never required for baseline functionality — `integration_generic` already covers any domain with zero dedicated plugin code.

---

## Plugin Types

| Type | Purpose | Distribution |
|------|---------|--------------|
| **Module** | Built-in domain expertise | Core repo (`modules/`) |
| **Integration plugin** | Specific integration diagnostics | External (`plugins/integrations/`) |
| **Infrastructure plugin** | Infrastructure health | External (`plugins/infrastructure/`) |

---

## Quick Start

### 1. Create Plugin Package

```bash
mkdir my-plugin && cd my-plugin
cat > pyproject.toml << 'EOF'
[project]
name = "ha-mcp-my-plugin"
version = "1.0.0"
description = "Custom plugin for MySystem"
dependencies = ["ha-mcp-core>=2.0.0"]

[project.entry-points."ha_mcp.plugins"]
my_plugin = "my_plugin.plugin:MyPlugin"
EOF

mkdir -p src/my_plugin
```

### 2. Implement Plugin Class

```python
# src/my_plugin/plugin.py
from ha_mcp.plugins import PluginBase, DetectionManifest
from ha_mcp.models import Tool, Resource, Finding, Recommendation, StagedEdit, EditType

class MyPlugin(PluginBase):
    name = "integrations.my_system"
    version = "1.0.0"
    description = "Specialized diagnostics for MySystem"
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

### 3. Implement Tools (Collector → Analyzer → Action)

A plugin tool that diagnoses a domain looks like:

```python
def get_tools(self) -> list[Tool]:
    return [Tool(
        name="diagnose_my_system",
        description="Diagnose MySystem integration health",
        input_schema={"type": "object", "properties": {"domain": {"type": "string"}}},
        handler=self.diagnose,
    )]

async def diagnose(self, params: dict) -> ToolResult:
    # 1. Collect observations
    observations = await self._collect(params)
    
    # 2. Analyze → Findings
    findings = await self._analyze(observations)
    
    # 3. Compile Recommendations → StagedEdits (if repair needed)
    recommendations = [self._recommend(f) for f in findings]
    
    return ToolResult(
        status="success",
        summary=f"Found {len(findings)} issues",
        findings=findings,
        recommendations=recommendations,
    )
```

---

## Plugin Manifest

```yaml
# manifest.yaml (bundled with plugin or in external_plugin_dirs)
name: "integrations.my_system"
version: "1.0.0"
description: "Specialized diagnostics for MySystem"
target_domains: ["my_system"]
required_providers: ["ha"]
detection:
  ha_integrations: ["my_system"]
  entities_pattern: ["sensor.my_system_*"]
  addons: []
  filesystem_paths: []
  docker_containers: []
```

---

## Publishing Plugins

### 1. Package Configuration

```toml
[project]
name = "ha-mcp-my-plugin"
version = "1.0.0"
description = "MySystem integration for HA MCP"
license = {text = "MIT"}
dependencies = ["ha-mcp-core>=2.0.0,<3.0.0"]

[project.entry-points."ha_mcp.plugins"]
my_plugin = "my_plugin.plugin:MyPlugin"
```

### 2. Build and Publish

```bash
pip install build twine
python -m build
twine upload dist/*
```

### 3. Installation

```bash
pip install ha-mcp-my-plugin
# Platform auto-discovers via entry points
```

---

## Conformance Testing

Run the conformance suite before publishing:

```bash
ha-mcp test-plugin /path/to/my-plugin
```

This verifies:
- Tool schema validity
- Required lifecycle methods
- No blocking calls in `initialize`
- Manifest completeness

---

## Best Practices

1. **Minimal dependencies** — only depend on `ha-mcp-core`
2. **Idempotent initialization** — guard against double-init
3. **Graceful degradation** — handle missing providers
4. **Structured logging** — use `structlog`
5. **Manifest-driven detection** — don't hardcode detection rules in Python

---

## Plugin Checklist

- [ ] Implements `PluginBase`
- [ ] Ships a `manifest.yaml`
- [ ] Declares `required_providers`
- [ ] Tools follow Collector → Analyzer → Action pattern
- [ ] Has unit tests with mocked providers/graph
- [ ] Documents configuration options
- [ ] Follows semantic versioning
- [ ] Declares `schema_version` compatibility in `Finding`s

---

*Plugins are the **extension mechanism**. Follow this guide to build plugins that integrate seamlessly with the platform without modifying core code.*
