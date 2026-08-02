# Provider Development Guide

## Overview

Providers are the **infrastructure layer** — they know how to talk to external systems (Home Assistant, Git, Docker, MQTT, etc.) but have **zero domain knowledge**. They provide raw data; modules consume it.

---

## When to Create a Provider

Create a provider when you need to:
- Connect to a new external system (API, database, message queue)
- Add a new data source for observations (logs, metrics, traces)
- Support a new infrastructure capability

Don't create a provider for:
- Domain-specific logic (that goes in modules/plugins)
- Business rules (that goes in modules)

---

## Provider Interface (Protocol)

```python
class Capability(Enum):
    DISCOVER = "discover"
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    STREAM = "stream"

class Provider(Protocol):
    name: str
    capabilities: frozenset[Capability]
    
    async def initialize(self, config: dict[str, Any]) -> None: ...
    async def shutdown(self) -> None: ...
    async def discover(self) -> list[str]: ...
    async def read(self, resource_id: str) -> Observation: ...
    async def write(self, resource_id: str, content: Any) -> None: ...
    async def execute(self, command: str, params: dict[str, Any]) -> Any: ...
    async def subscribe(self, filter: dict[str, Any], callback: Callable) -> None: ...
```

**Key principle**: Providers are Protocols, not ABCs. Implement whichever subset is meaningful — no `NotImplementedError` stubs required.

---

## Quick Start

### 1. Create Provider Package

```bash
mkdir my-provider && cd my-provider
cat > pyproject.toml << 'EOF'
[project]
name = "ha-mcp-my-provider"
version = "1.0.0"
description = "Provider for MySystem API"
dependencies = ["ha-mcp-core>=2.0.0", "httpx>=0.25"]

[project.entry-points."ha_mcp.providers"]
my_provider = "my_provider.provider:MyProvider"
EOF

mkdir -p src/my_provider
```

### 2. Implement Provider

```python
# src/my_provider/provider.py
from ha_mcp.models import Capability, Observation, ObservationType

class MyProvider:
    name = "mysystem"
    capabilities = frozenset({Capability.READ, Capability.STREAM})
    
    async def initialize(self, config: dict[str, Any]) -> None:
        self.config = config
        # Setup client, verify connection
    
    async def shutdown(self) -> None:
        # Cleanup
    
    async def read(self, resource_id: str) -> Observation:
        # Return observation for resource
        pass
    
    async def subscribe(self, filter: dict, callback) -> None:
        # Stream observations
        pass
```

### 3. Register via Entry Point

```toml
[project.entry-points."ha_mcp.providers"]
my_provider = "my_provider.provider:MyProvider"
```

---

## Provider Checklist

- [ ] Implements `Provider` protocol
- [ ] Declares accurate `capabilities` as `frozenset[Capability]`
- [ ] Validates configuration in `initialize`
- [ ] Implements `shutdown` for cleanup
- [ ] Uses connection pooling and timeouts
- [ ] Implements retry logic for transient failures
- [ ] Uses structured logging
- [ ] Handles authentication securely (no tokens in logs)
- [ ] Documents all configuration options
- [ ] Follows semantic versioning
- [ ] Registers via entry point `ha_mcp.providers`

---

*Providers are the **foundation** of the platform. Keep them simple, robust, and focused on infrastructure communication only.*
