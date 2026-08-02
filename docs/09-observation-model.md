# Observation Model

## Overview

The Observation Model unifies **all telemetry** into a single type. Instead of separate systems for logs, metrics, traces, history, and events, everything becomes an `Observation` with a common structure.

---

## Why Unified Observations?

| Traditional | Unified |
|-------------|---------|
| Separate tools for logs, metrics, traces | Single query interface |
| Hard to correlate across types | Built-in correlation via `subject_id` |
| Different retention policies | Consistent lifecycle |
| Siloed analysis | Cross-observation patterns |
| Multiple APIs to learn | One Observation API |

---

## Observation

```python
@dataclass(frozen=True)
class Observation:
    id: str
    type: ObservationType   # STATE, LOG, METRIC, TRACE, HISTORY, EVENT
    subject_id: str          # GraphNode.id (single subject)
    timestamp: datetime
    data: dict[str, Any]     # Type-specific payload
    source: str              # Provider name, e.g. "ha", "docker", "logs"

class ObservationType(Enum):
    STATE = "state"
    LOG = "log"
    METRIC = "metric"
    TRACE = "trace"
    HISTORY = "history"
    EVENT = "event"
```

**Key points**:
- Single `subject_id` — the GraphNode this observation is about
- `data` is a dict holding type-specific payload
- `source` identifies which Provider produced it
- `frozen=True` — observations are immutable facts

---

## Payload Examples

### LogPayload
```python
{
    "level": "ERROR",
    "message": "Tesla API request failed: 401 Unauthorized",
    "logger": "homeassistant.components.tesla",
    "structured_data": {"endpoint": "/api/vehicles", "status": 401}
}
```

### MetricPayload
```python
{
    "name": "cpu_usage",
    "value": 87.5,
    "unit": "percent",
    "labels": {"container": "ha-mqtt"}
}
```

### HistoryPayload
```python
{
    "entity_id": "sensor.tesla_battery_level",
    "old_state": 85,
    "new_state": 84,
    "duration": "3600s",
    "trigger": "vehicle_charging_stopped"
}
```

### TracePayload
```python
{
    "automation_id": "automation.tesla_charging",
    "trace_id": "trace-abc",
    "span_id": "span-1",
    "operation": "condition",
    "duration": "0.8s",
    "status": "FAILED",
    "error_message": "Entity sensor.tesla_battery_level unavailable"
}
```

### TelemetryPayload
```python
{
    "source": "tesla",
    "data": {
        "battery_level": 84,
        "charging_state": "Stopped",
        "charge_limit": 90
    }
}
```

### EventPayload
```python
{
    "event_type": "automation_triggered",
    "data": {"automation_id": "automation.tesla_charging", "trigger": "time"},
    "context": {"user_id": null, "parent_id": null}
}
```

---

## Ingestion Pipeline

```
Providers → Collector → Observation → GraphRepository (index by subject_id)
```

1. **Providers** produce raw data (REST responses, log lines, MQTT messages, etc.)
2. **Collectors** normalize into `Observation` instances
3. **GraphRepository** indexes by `subject_id` for fast lookup

---

## Queries

```python
class ObservationQuery:
    subject_id: str | None = None
    types: list[ObservationType] | None = None
    since: datetime | None = None
    until: datetime | None = None
    source: str | None = None
    limit: int = 1000
```

---

*Unified observations enable cross-type correlation through `subject_id`, a single query interface, and consistent retention. No separate class hierarchy, no separate storage per type.*
