# Resource Model

## Overview

The Resource Model defines how every entity in the system is represented via `GraphNode` and `ResourceKind`. This is the **single abstraction** that makes the platform backend-agnostic.

---

## GraphNode

```python
@dataclass(frozen=True)
class GraphNode:
    id: str                              # HA's unique_id (or entity_id for entities without unique_id)
    resource_kind: ResourceKind
    integration_domain: str | None = None # e.g., "tesla", "mqtt", "homeassistant"
    attributes: dict[str, Any] = field(default_factory=dict)
```

**Key points**:
- `id` reuses HA's own `unique_id` — no invented UUID scheme
- `integration_domain` comes from HA's config entry / device registry
- `attributes` holds raw HA attributes, config, state, etc.
- No lifecycle states, no version field, no relationships stored on the node

---

## ResourceKind (Flat Enum)

```
ResourceKind:
  ENTITY          # sensor.temperature, binary_sensor.motion
  DEVICE          # device_tracker, person, zone
  WORKFLOW        # automation.morning, script.notify
  VISUALIZATION   # dashboard.energy, view.living_room
  EXECUTION       # addon.mosquitto, container.ha-mqtt
  CONFIGURATION   # configuration.yaml, secrets.yaml, package files
  TEMPLATE        # Jinja2 templates in automations/scripts/dashboards
  INTEGRATION     # integration.tesla, integration.mqtt
  SERVICE         # service calls, service definitions
```

**No inheritance, no abstract base class, no versioning.**

---

## Query Patterns

```python
# All entities
nodes = graph.find({"resource_kind": ResourceKind.ENTITY})

# All workflows in "climate" category (via attributes)
nodes = graph.find({"resource_kind": ResourceKind.WORKFLOW, "attributes.category": "climate"})

# All Tesla entities
tesla_nodes = graph.find({"integration_domain": "tesla"})

# Unavailable entities
unavailable = graph.find({
    "resource_kind": ResourceKind.ENTITY,
    "attributes.availability": "unavailable"
})
```

---

## Adapter Mapping

| HA Concept | ResourceKind | Key Fields in attributes |
|------------|--------------|--------------------------|
| `sensor.temperature` | `ENTITY` | state, attributes, last_changed, availability |
| `binary_sensor.motion` | `ENTITY` | state, availability |
| `device_tracker.phone` | `DEVICE` | state, attributes |
| `automation.morning` | `WORKFLOW` | triggers, conditions, actions, trace |
| `script.notify` | `WORKFLOW` | sequence, variables |
| `dashboard.energy` | `VISUALIZATION` | views, cards, theme |
| `addon.mosquitto` | `EXECUTION` | status, config, logs |
| `configuration.yaml` | `CONFIGURATION` | content, parsed, schema_version |
| `template.battery` | `TEMPLATE` | source, parameters, dependencies |
| `integration.tesla` | `INTEGRATION` | domain, version, config_entries, provides |
| `service.light.turn_on` | `SERVICE` | domain, service, schema |

---

*This resource model ensures **consistent identity**, **clear classification**, and **backend-agnostic operations** across all modules. The `GraphNode` + `resource_kind` pair replaces the v1 `AutomationObject`-style per-domain wrappers.*
