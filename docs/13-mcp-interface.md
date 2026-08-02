# MCP Interface

## Overview

The MCP (Model Context Protocol) interface is the **primary interface** to the platform. It exposes modules' and plugins' capabilities as MCP tools and resources.

---

## Tool Surface

Tools expose **expertise, not APIs**. The tool surface stays deliberately named — not assembled from introspection.

| MCP Tool | Module | Description |
|----------|--------|-------------|
| `diagnose_dashboard(name_or_id)` | dashboards | Comprehensive dashboard health check |
| `find_broken_dashboards()` | dashboards | All dashboards with issues |
| `validate_dashboard_yaml(yaml_content)` | dashboards | Card validation, entity references, templates |
| `analyze_dashboard_performance(dashboard_id)` | dashboards | Card render times, entity count, update frequency |
| `analyze_automation(automation_id)` | automations | Full analysis: triggers, conditions, actions, traces |
| `find_broken_automations()` | automations | Missing entities, invalid templates, deprecated features |
| `simulate_automation(...)` | automations | Dry-run with hypothetical state changes |
| `find_unused_entities()` | entities | Entities not referenced anywhere |
| `analyze_entity_health(entity_id)` | entities | Availability, state history, attribute analysis |
| `get_entity_dependencies(entity_id)` | entities | Full dependency chain |
| `validate_template(template_string, context)` | templates | Syntax + runtime validation |
| `explain_template(template_string)` | templates | What the template does in plain English |
| `validate_yaml(path_or_content)` | yaml | Syntax + Home Assistant schema validation |
| `search_configuration(query, type="all")` | search | Semantic search across all config |
| `build_context(problem, scope="auto")` | context | One-call context gathering for AI |
| `repair_system()` | repair | Comprehensive repair scan |
| `repair_dashboard(dashboard_id)` | repair | Fix specific dashboard |
| `transaction_begin(description)` | transaction | Start a transaction |
| `transaction_stage(edit)` | transaction | Stage an edit |
| `transaction_diff()` | transaction | Show staged changes |
| `transaction_validate()` | transaction | Dry-run validation |
| `transaction_commit(message)` | transaction | Apply all staged changes atomically |
| `transaction_verify()` | transaction | Re-run original check to confirm resolution |
| `transaction_rollback()` | transaction | Discard all staged changes |
| `transaction_status()` | transaction | Current transaction state |
| `analyze_template_costs()` | cost | Most expensive templates |
| `analyze_dashboard_costs()` | cost | Most expensive dashboards |
| `get_resource_report()` | cost | System-wide resource analysis |
| `explain_automation_failure(id, trace_id)` | explain | Why it didn't run/failed |
| `explain_entity(entity_id)` | explain | Why entity exists, what creates it, what uses it |
| `full_system_diagnosis()` | diagnostics | Comprehensive health check |
| `diagnose_integration(domain)` | diagnostics / integration_generic | Integration-specific diagnosis |
| `health_score()` | diagnostics | Overall system health 0-100 |
| `list_integrations()` | integration_generic | All installed integrations |
| `find_unhealthy_integrations()` | integration_generic | Domains with setup errors or low availability |
| `subscribe_events(filter, duration)` | events | Subscribe to event stream |
| `replay_events(filter, since)` | events | Historical event replay |

---

## MCP Resources

### Live Event Streams

```
ha://events/state_changes?entity_ids=sensor.temp,sensor.humidity
ha://events/automation_executions?automation_ids=automation.morning
ha://events/logs?level=ERROR&since=1h
ha://events/mqtt?topic=homeassistant/#
ha://events/docker?container=ha-mqtt
```

### Resource Access

```
ha://resources/{node_id}
ha://resources/by-domain/tesla
ha://resources/search?query=battery+level
```

---

## Tool Response Format

```python
@dataclass
class ToolResult:
    status: Literal["success", "warning", "error", "info"]
    summary: str
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    transaction_id: str | None = None
```

---

## Error Handling

| Error Type | Meaning |
|------------|---------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `TRANSACTION_FAILED` | Transaction commit failed |
| `PROVIDER_ERROR` | Provider error |
| `INTERNAL_ERROR` | Unexpected error |

---

*The MCP interface is thin. It translates external requests → tool calls → Modules. Intent is an internal dispatch convention only — never exposed as the MCP interface itself.*
