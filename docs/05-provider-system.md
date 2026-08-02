# Provider System

## Overview

Providers are the **infrastructure layer** — they know how to talk to external systems but have **zero domain knowledge**. They provide raw data; modules consume it.

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

**Key principle**: Providers are Protocols, not ABCs. A provider implements whichever subset is meaningful for it (Git doesn't `subscribe()`; that's fine) instead of stubbing `NotImplementedError` for the rest.

---

## Provider Registry

```python
class ProviderRegistry:
    def __init__(self):
        self._providers: dict[str, Provider] = {}
    
    def register(self, provider: Provider) -> None:
        self._providers[provider.name] = provider
    
    def get(self, name: str) -> Provider:
        return self._providers[name]
    
    async def initialize_all(self, config: dict[str, Any]) -> None:
        for provider in self._providers.values():
            await provider.initialize(config.get(provider.name, {}))
    
    async def shutdown_all(self) -> None:
        for provider in reversed(list(self._providers.values())):
            await provider.shutdown()
```

---

## Core Providers

### HA Provider (`HAProvider`)

**Purpose**: Home Assistant REST API + WebSocket.

```python
class HAProvider:
    name = "ha"
    capabilities = frozenset({
        Capability.DISCOVER, Capability.READ, Capability.WRITE,
        Capability.EXECUTE, Capability.STREAM
    })
```

**Configuration**:
```yaml
providers:
  ha:
    url: "http://homeassistant.local:8123"
    token: "${HA_TOKEN}"
    verify_ssl: true
    websocket: true
    cache_ttl_seconds: 60
```

---

### Git Provider (`GitProvider`)

**Purpose**: Repository operations using dulwich (pure Python).

```python
class GitProvider:
    name = "git"
    capabilities = frozenset({
        Capability.DISCOVER, Capability.READ, Capability.WRITE
    })
```

**Configuration**:
```yaml
providers:
  git:
    repo_path: "/config"
```

---

### Filesystem Provider (`FilesystemProvider`)

**Purpose**: Safe file I/O with sandboxing.

```python
class FilesystemProvider:
    name = "filesystem"
    capabilities = frozenset({
        Capability.READ, Capability.WRITE
    })
```

**Configuration**:
```yaml
providers:
  filesystem:
    base_path: "/config"
    backup_before_write: true
```

---

### Docker Provider (`DockerProvider`)

**Purpose**: Docker Engine API (socket or remote).

```python
class DockerProvider:
    name = "docker"
    capabilities = frozenset({
        Capability.DISCOVER, Capability.READ, Capability.EXECUTE, Capability.STREAM
    })
```

**Configuration**:
```yaml
providers:
  docker:
    socket: "/var/run/docker.sock"
```

---

### MQTT Provider (`MQTTProvider`)

**Purpose**: MQTT broker connection.

```python
class MQTTProvider:
    name = "mqtt"
    capabilities = frozenset({
        Capability.DISCOVER, Capability.READ, Capability.WRITE, Capability.STREAM
    })
```

**Configuration**:
```yaml
providers:
  mqtt:
    broker: "mqtt://homeassistant.local:1883"
```

---

### Logs Provider (`LogsProvider`)

**Purpose**: Unified log aggregation.

```python
class LogsProvider:
    name = "logs"
    capabilities = frozenset({
        Capability.READ, Capability.STREAM
    })
```

**Configuration**:
```yaml
providers:
  logs:
    source: "file"
    path: "/config/home-assistant.log"
```

---

### Events Provider (`EventsProvider`)

**Purpose**: Unified event bus.

```python
class EventsProvider:
    name = "events"
    capabilities = frozenset({
        Capability.STREAM
    })
```

**Configuration**:
```yaml
providers:
  events:
    buffer_size: 10000
```

---

## Error Handling

```python
class ProviderError(Exception):
    def __init__(self, provider: str, operation: str, message: str, recoverable: bool = True):
        self.provider = provider
        self.operation = operation
        self.message = message
        self.recoverable = recoverable
        super().__init__(f"{provider}.{operation}: {message}")
```

---

*Providers are the **only layer** that talks to external infrastructure. All domain logic lives in modules and plugins that consume providers.*
