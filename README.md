# Home Assistant MCP Server

> **AI sysadmin for Home Assistant** — analysis platform exposing diagnostics, automation health, entity monitoring, dashboard analysis, and configuration search via the Model Context Protocol.

## Features

- **Entity Health Analysis** — detect stale/unavailable entities, unknown states, missing attributes
- **Automation Diagnostics** — find disabled automations, missing triggers, invalid configurations
- **Dashboard Analysis** — detect deprecated cards, missing views
- **System Health Score** — 0-100 health score across all entities
- **Configuration Search** — semantic search across entity IDs, friendly names, and states
- **Scene Analysis** — detect empty or misconfigured scenes
- **Template Analysis** — detect templates without Jinja2 syntax
- **YAML Validation** — detect empty or invalid YAML configurations
- **Transaction Safety** — staged edits with validate/commit/rollback/verify semantics
- **Multi-Provider Support** — HA REST/WebSocket, Git, Filesystem, Docker, MQTT, Logs, Events
- **Plugin Ecosystem** — manifest-driven plugin discovery via entry points

## Requirements

- Python 3.11+
- Home Assistant instance (for HA provider functionality)
- pip/venv for installation

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd mcp_server_ha

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Configuration

The server is configured via environment variables or a config file passed to the HA provider.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HA_URL` | Home Assistant URL | `http://homeassistant.local:8123` |
| `HA_TOKEN` | Long-lived access token | (required for HA features) |
| `HA_VERIFY_SSL` | Verify SSL certificates | `true` |

### Example Configuration

```python
config = {
    "ha": {
        "url": "http://homeassistant.local:8123",
        "token": "your-long-lived-access-token",
        "verify_ssl": True,
    }
}
```

## Running the Server

### As a Standalone MCP Server

```bash
# Start the MCP server (Streamable HTTP)
ha-mcp

# Or directly with Python
python -m ha_mcp.server
```

The server listens on `http://localhost:8090/mcp` using Streamable HTTP. Set `HA_URL`,
`HA_TOKEN`, and optionally `HA_VERIFY_SSL` before starting it.

### As a Library

```python
import asyncio
from ha_mcp.app import App
from ha_mcp.providers.ha import HAProvider
from ha_mcp.modules.entities.module import EntitiesModule

async def main():
    app = App()
    provider = HAProvider()
    module = EntitiesModule(provider)
    
    app.register_provider(provider)
    app.register_module("entities", module)
    await app.initialize({"ha": {"url": "http://homeassistant.local:8123", "token": "..."}})
    
    result = await app.run_module("entities", requested_by="user")
    for finding in result.findings:
        print(f"[{finding.severity}] {finding.message}")
    
    await app.shutdown()

asyncio.run(main())
```

## Connecting to MCP Clients

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "ha-mcp": {
      "command": "ha-mcp",
      "env": {
        "HA_URL": "http://homeassistant.local:8123",
        "HA_TOKEN": "your-long-lived-access-token"
      }
    }
  }
}
```

### Claude Code (CLI)

```bash
claude --mcp "ha-mcp:ha-mcp"
```

### Other MCP Clients

Any MCP-compatible client can connect to `http://localhost:8090/mcp` using Streamable HTTP.

### VS Code

When the `ha-mcp` server is connected in VS Code, open Copilot Chat in Agent mode and
ask for one of the commands below in plain language. Copilot selects the matching MCP
tool and supplies the arguments from your request. For example:

```text
Run health_score.
Find broken automations.
Analyze automation automation.morning.
Validate this YAML: automation:\n  - alias: Kitchen lights
```

For tools with a required ID or value, include it in the prompt. For example, say
`Diagnose dashboard lovelace-main` or `Search Home Assistant configuration for Tesla`.
Review the result before running transaction commit or repair commands.

## Docker

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build manually
docker build -t ha-mcp .
docker run -e HA_URL=http://homeassistant:8123 -e HA_TOKEN=your-token ha-mcp
```

## Home Assistant Add-on

You can install this as a Home Assistant Add-on:

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**
2. Click the menu (three dots) → **Repositories**
3. Add this repository URL
4. Find **HA MCP Server** and click **Install**
5. Configure your `HA_URL` and `HA_TOKEN`
6. Start the add-on

The add-on runs as a service on the same network as Home Assistant and exposes the MCP interface over stdio.

## Available MCP Tools

Use the command name in Copilot Chat, followed by its required values. Empty arguments
mean the command can be run without parameters.

### Entity and system health

| Command | Required arguments | Example VS Code chat prompt |
|---------|--------------------|-----------------------------|
| `health_score` | None | `Run health_score.` |
| `full_system_diagnosis` | None | `Run a full system diagnosis.` |
| `analyze_entity_health` | `entity_id` | `Analyze entity health for sensor.living_room_temperature.` |
| `find_unused_entities` | None | `Find unused entities.` |
| `get_entity_dependencies` | `entity_id` | `Show dependencies for light.kitchen.` |
| `search_configuration` | `query` | `Search configuration for Tesla charging.` |
| `build_context` | `problem`; optional `scope` | `Build context for why lights are unavailable, scoped to lighting.` |

### Automations, dashboards, scenes, and configuration

| Command | Required arguments | Example VS Code chat prompt |
|---------|--------------------|-----------------------------|
| `analyze_automation` | `automation_id` | `Analyze automation automation.morning.` |
| `simulate_automation` | `automation_id` | `Simulate automation automation.morning.` |
| `find_broken_automations` | None | `Find broken automations.` |
| `diagnose_dashboard` | `dashboard_id` | `Diagnose dashboard lovelace-main.` |
| `validate_dashboard_yaml` | `yaml_content` | `Validate this dashboard YAML: <YAML content>.` |
| `find_broken_dashboards` | None | `Find broken dashboards.` |
| `repair_dashboard` | `dashboard_id` | `Repair dashboard lovelace-main.` |
| `analyze_scene` | `scene_id` | `Analyze scene scene.evening.` |
| `validate_template` | `template_string` | `Validate template {{ states('sensor.temperature') }}.` |
| `explain_template` | `template_string` | `Explain template {{ is_state('binary_sensor.door', 'on') }}.` |
| `validate_yaml` | `path_or_content` | `Validate this YAML: <YAML content>.` |

### Integrations and events

| Command | Required arguments | Example VS Code chat prompt |
|---------|--------------------|-----------------------------|
| `diagnose_integration` | `domain` | `Diagnose the mqtt integration.` |
| `list_integrations` | None | `List installed integrations.` |
| `find_unhealthy_integrations` | None | `Find unhealthy integrations.` |
| `subscribe_events` | `filter`; optional `duration` | `Subscribe to automation events for 60 seconds.` |
| `replay_events` | `filter`, `since` | `Replay state-change events since 2026-08-01T00:00:00Z.` |

### Repair and transactions

| Command | Required arguments | Example VS Code chat prompt |
|---------|--------------------|-----------------------------|
| `repair_system` | None | `Run a system repair scan.` |
| `transaction_begin` | `description` | `Start a transaction to update kitchen automation.` |
| `transaction_stage` | `transaction_id`, `edit` | `Stage this edit in transaction <ID>: <edit object>.` |
| `transaction_diff` | `transaction_id` | `Show the diff for transaction <ID>.` |
| `transaction_validate` | `transaction_id` | `Validate transaction <ID>.` |
| `transaction_commit` | `transaction_id` | `Commit transaction <ID>.` |
| `transaction_verify` | `transaction_id` | `Verify transaction <ID>.` |
| `transaction_rollback` | `transaction_id` | `Roll back transaction <ID>.` |
| `transaction_status` | `transaction_id` | `Show the status of transaction <ID>.` |

The normal transaction sequence is: `transaction_begin`, `transaction_stage`,
`transaction_diff`, `transaction_validate`, `transaction_commit`, then
`transaction_verify`. Use `transaction_rollback` before committing when you need to
discard staged changes.

## Project Structure

```
src/ha_mcp/
├── __init__.py
├── app.py                    # Application orchestrator
├── config.py                 # Pydantic-settings configuration
├── logging_config.py         # Structlog configuration
├── models/                   # Frozen domain models
│   ├── graph_node.py
│   ├── observation.py
│   ├── finding.py
│   ├── recommendation.py
│   ├── staged_edit.py
│   ├── tool_result.py
│   ├── provider_protocol.py  # Provider Protocol with Capability enum
│   └── action.py
├── providers/                # Transport implementations
│   ├── base.py               # ProviderRegistry
│   ├── ha/                   # Home Assistant REST/WebSocket
│   ├── git/                  # Git operations via dulwich
│   ├── filesystem/           # Local filesystem
│   ├── docker/               # Docker SDK
│   ├── mqtt/                 # MQTT via aiomqtt
│   ├── logs/                 # Log file reading
│   └── events/               # Event streaming
├── modules/                  # Analysis modules
│   ├── entities/             # Entity health analysis
│   ├── automations/          # Automation diagnostics
│   ├── dashboards/           # Dashboard analysis
│   ├── diagnostics/          # System health score
│   ├── search/               # Configuration search
│   ├── scenes/               # Scene analysis
│   ├── templates/            # Template analysis
│   └── yaml/                 # YAML validation
├── graph/                    # GraphRepository Protocol + NetworkX impl
│   ├── graph_repository.py
│   └── graph_repository_impl.py
├── analysis/                 # Collector/Analyzer Protocols
│   └── pipeline.py
├── transaction/              # TransactionManager
│   └── transaction_manager.py
├── plugins/                  # Plugin system
│   ├── manifest.py
│   └── loader.py
└── server/                   # MCP stdio server
    └── __init__.py
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Adding a New Module

1. Create `src/ha_mcp/modules/your_module/` with:
   - `collector.py` — implements `Collector` Protocol
   - `analyzer.py` — implements `Analyzer` Protocol
   - `module.py` — wires collector + analyzer + action
   - `__init__.py`

2. The module is auto-discovered by `App.auto_register_modules()`

3. Add MCP tool in `src/ha_mcp/server/__init__.py`

### Adding a Plugin

1. Create a package with `PluginManifest`:
   ```python
   from ha_mcp.plugins import PluginManifest
   
   manifest = PluginManifest(
       name="my-plugin",
       version="1.0.0",
       description="My custom plugin",
       author="Author",
       capabilities=frozenset({"read", "write"}),
       entry_point="my_plugin.module",
   )
   ```

2. Register in `pyproject.toml`:
   ```toml
   [project.entry-points."ha_mcp.plugins"]
   my-plugin = "my_plugin"
   ```

## Architecture

See `docs/02-architecture.md` for the v2.2 architecture specification.

### Key Constraints

- **No LLM in core** — all analysis is deterministic
- **Single mutation path** — Collector → Analyzer → Finding → Recommendation → Action → StagedEdit → TransactionManager
- **Frozen domain models** — `GraphNode`, `Observation`, `Finding`, `Recommendation`, `StagedEdit` are immutable
- **Provider Protocol** — all transports implement `Provider` with `frozenset[Capability]`
- **Intent is internal** — never exposed through MCP

## Testing

```bash
# All tests
pytest tests/ -v

# Contract tests only
pytest tests/contract/ -v

# Unit tests only
pytest tests/unit/ -v
```

## CI/CD

GitHub Actions runs tests on Python 3.11, 3.12, 3.13 and linting with ruff on every push and PR.

## License

MIT
