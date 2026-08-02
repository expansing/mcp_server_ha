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
# Start the MCP server (stdio transport)
ha-mcp

# Or directly with Python
python -m ha_mcp.server
```

The server uses **stdio** transport by default, communicating via JSON-RPC over stdin/stdout.

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

The server implements the standard MCP protocol over stdio. Any MCP-compatible client can connect by spawning the `ha-mcp` process.

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

| Tool | Description |
|------|-------------|
| `analyze_entity_health` | Analyze health of a specific entity |
| `find_unused_entities` | Find entities not referenced anywhere |
| `health_score` | Get overall system health score 0-100 |
| `analyze_automation` | Analyze an automation for issues |
| `find_broken_automations` | Find automations with missing triggers or disabled state |
| `analyze_dashboard` | Analyze a dashboard for deprecated cards or missing views |
| `find_broken_dashboards` | Find dashboards with issues |
| `full_system_diagnosis` | Comprehensive health check across all modules |
| `search_configuration` | Semantic search across all configuration |
| `analyze_scene` | Analyze a scene for issues |
| `transaction_begin` | Start a new transaction for staging edits |
| `transaction_commit` | Commit the current transaction |
| `transaction_rollback` | Rollback the current transaction |
| `transaction_status` | Get the status of a transaction |

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
