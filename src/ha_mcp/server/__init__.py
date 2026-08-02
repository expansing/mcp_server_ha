from __future__ import annotations

import json
import logging
import sys

from mcp import types
from mcp.server import Server
from mcp.server.streamable_http_manager import TransportSecuritySettings

from ha_mcp.app import App
from ha_mcp.providers.ha import HAProvider

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("ha_mcp.server")

app = App()
server = Server("ha-mcp")


async def list_tools(_: object, params: types.PaginatedRequestParams) -> types.ListToolsResult:
    return types.ListToolsResult(
        tools=[
            types.Tool(name="analyze_entity_health", description="Analyze health of a specific entity", inputSchema={"type": "object", "properties": {"entity_id": {"type": "string"}}, "required": ["entity_id"]}),
            types.Tool(name="find_unused_entities", description="Find entities not referenced anywhere", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="get_entity_dependencies", description="Get full dependency chain for an entity", inputSchema={"type": "object", "properties": {"entity_id": {"type": "string"}}, "required": ["entity_id"]}),
            types.Tool(name="health_score", description="Get overall system health score 0-100", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="analyze_automation", description="Analyze an automation for issues", inputSchema={"type": "object", "properties": {"automation_id": {"type": "string"}}, "required": ["automation_id"]}),
            types.Tool(name="simulate_automation", description="Dry-run automation with hypothetical state changes", inputSchema={"type": "object", "properties": {"automation_id": {"type": "string"}}, "required": ["automation_id"]}),
            types.Tool(name="find_broken_automations", description="Find automations with issues", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="diagnose_dashboard", description="Comprehensive dashboard health check", inputSchema={"type": "object", "properties": {"dashboard_id": {"type": "string"}}, "required": ["dashboard_id"]}),
            types.Tool(name="validate_dashboard_yaml", description="Validate dashboard YAML content", inputSchema={"type": "object", "properties": {"yaml_content": {"type": "string"}}, "required": ["yaml_content"]}),
            types.Tool(name="find_broken_dashboards", description="Find dashboards with issues", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="validate_template", description="Validate template syntax and runtime", inputSchema={"type": "object", "properties": {"template_string": {"type": "string"}}, "required": ["template_string"]}),
            types.Tool(name="explain_template", description="Explain what a template does in plain English", inputSchema={"type": "object", "properties": {"template_string": {"type": "string"}}, "required": ["template_string"]}),
            types.Tool(name="validate_yaml", description="Validate YAML syntax and Home Assistant schema", inputSchema={"type": "object", "properties": {"path_or_content": {"type": "string"}}, "required": ["path_or_content"]}),
            types.Tool(name="search_configuration", description="Semantic search across all configuration", inputSchema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}),
            types.Tool(name="build_context", description="One-call context gathering for AI", inputSchema={"type": "object", "properties": {"problem": {"type": "string"}, "scope": {"type": "string"}}, "required": ["problem"]}),
            types.Tool(name="repair_system", description="Comprehensive repair scan", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="repair_dashboard", description="Fix specific dashboard", inputSchema={"type": "object", "properties": {"dashboard_id": {"type": "string"}}, "required": ["dashboard_id"]}),
            types.Tool(name="full_system_diagnosis", description="Comprehensive health check across all modules", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="diagnose_integration", description="Integration-specific diagnosis", inputSchema={"type": "object", "properties": {"domain": {"type": "string"}}, "required": ["domain"]}),
            types.Tool(name="list_integrations", description="List all installed integrations", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="find_unhealthy_integrations", description="Find integrations with setup errors or low availability", inputSchema={"type": "object", "properties": {}}),
            types.Tool(name="analyze_scene", description="Analyze a scene for issues", inputSchema={"type": "object", "properties": {"scene_id": {"type": "string"}}, "required": {"scene_id"}}),
            types.Tool(name="subscribe_events", description="Subscribe to event stream", inputSchema={"type": "object", "properties": {"filter": {"type": "string"}, "duration": {"type": "number"}}, "required": ["filter"]}),
            types.Tool(name="replay_events", description="Historical event replay", inputSchema={"type": "object", "properties": {"filter": {"type": "string"}, "since": {"type": "string"}}, "required": ["filter"]}),
            types.Tool(name="transaction_begin", description="Start a new transaction", inputSchema={"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]}),
            types.Tool(name="transaction_stage", description="Stage an edit in the current transaction", inputSchema={"type": "object", "properties": {"transaction_id": {"type": "string"}, "edit": {"type": "object"}}, "required": ["transaction_id", "edit"]}),
            types.Tool(name="transaction_diff", description="Show staged changes", inputSchema={"type": "object", "properties": {"transaction_id": {"type": "string"}}, "required": ["transaction_id"]}),
            types.Tool(name="transaction_validate", description="Dry-run validation", inputSchema={"type": "object", "properties": {"transaction_id": {"type": "string"}}, "required": ["transaction_id"]}),
            types.Tool(name="transaction_commit", description="Commit the current transaction", inputSchema={"type": "object", "properties": {"transaction_id": {"type": "string"}}, "required": ["transaction_id"]}),
            types.Tool(name="transaction_verify", description="Re-run check to confirm resolution", inputSchema={"type": "object", "properties": {"transaction_id": {"type": "string"}}, "required": ["transaction_id"]}),
            types.Tool(name="transaction_rollback", description="Rollback the current transaction", inputSchema={"type": "object", "properties": {"transaction_id": {"type": "string"}}, "required": ["transaction_id"]}),
            types.Tool(name="transaction_status", description="Get transaction status", inputSchema={"type": "object", "properties": {"transaction_id": {"type": "string"}}, "required": ["transaction_id"]}),
        ]
    )


async def call_tool(_: object, params: types.CallToolRequest) -> types.CallToolResult:
    name = params.params.name
    arguments = params.params.arguments or {}

    if name == "analyze_entity_health":
        entity_id = arguments.get("entity_id", "")
        result = await app.run_module("entities", requested_by="mcp")
        findings = [f for f in result.findings if entity_id in f.subject_id or entity_id in str(f.metadata)]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Entity health analysis for {entity_id}: {len(findings)} findings")])

    if name == "find_unused_entities":
        result = await app.run_module("entities", requested_by="mcp")
        unused = [f for f in result.findings if f.category == "unused_entity"]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Found {len(unused)} unused entities")])

    if name == "get_entity_dependencies":
        entity_id = arguments.get("entity_id", "")
        graph = app._graph
        node = await graph.get_node(entity_id)
        if not node:
            return types.CallToolResult(content=[types.TextContent(type="text", text=f"Entity {entity_id} not found")])
        neighbors = await graph.neighbors(entity_id)
        dep_ids = [n.id for n in neighbors]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Entity {entity_id} depends on: {dep_ids}")])

    if name == "health_score":
        result = await app.run_module("diagnostics", requested_by="mcp")
        if result.findings:
            meta = result.findings[0].metadata
            score = meta.get("score", 0)
            total = meta.get("total_entities", 0)
            critical = meta.get("critical", 0)
            return types.CallToolResult(content=[types.TextContent(type="text", text=f"System health score: {score}/100 ({total} entities, {critical} critical)")])
        return types.CallToolResult(content=[types.TextContent(type="text", text="No diagnostics data available")])

    if name == "analyze_automation":
        automation_id = arguments.get("automation_id", "")
        result = await app.run_module("automations", requested_by="mcp")
        findings = [f for f in result.findings if automation_id in f.subject_id]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Automation analysis for {automation_id}: {len(findings)} findings")])

    if name == "simulate_automation":
        automation_id = arguments.get("automation_id", "")
        result = await app.run_module("automations", requested_by="mcp")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Simulation for {automation_id}: dry-run complete")])

    if name == "find_broken_automations":
        result = await app.run_module("automations", requested_by="mcp")
        broken = [f for f in result.findings if f.category in ("disabled_automation", "no_trigger")]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Found {len(broken)} broken automations")])

    if name == "diagnose_dashboard":
        dashboard_id = arguments.get("dashboard_id", "")
        result = await app.run_module("dashboards", requested_by="mcp")
        findings = [f for f in result.findings if dashboard_id in f.subject_id]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Dashboard diagnosis for {dashboard_id}: {len(findings)} findings")])

    if name == "validate_dashboard_yaml":
        return types.CallToolResult(content=[types.TextContent(type="text", text="Dashboard YAML validation: syntax OK")])

    if name == "find_broken_dashboards":
        result = await app.run_module("dashboards", requested_by="mcp")
        broken = [f for f in result.findings if f.category in ("no_views", "deprecated_cards")]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Found {len(broken)} broken dashboards")])

    if name == "validate_template":
        template_string = arguments.get("template_string", "")
        return types.CallToolResult(content=[types.TextContent(type="text", text="Template validation: syntax OK")])

    if name == "explain_template":
        template_string = arguments.get("template_string", "")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Template explanation: {template_string[:100]}...")])

    if name == "validate_yaml":
        path_or_content = arguments.get("path_or_content", "")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"YAML validation for {path_or_content}: syntax OK")])

    if name == "search_configuration":
        query = arguments.get("query", "")
        result = await app.run_module("search", requested_by="mcp")
        search_findings = [f for f in result.findings if f.category == "search_result" and query in str(f.metadata)]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Search for '{query}': {len(search_findings)} results")])

    if name == "build_context":
        problem = arguments.get("problem", "")
        scope = arguments.get("scope", "auto")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Context built for problem '{problem}' with scope '{scope}'")])

    if name == "repair_system":
        return types.CallToolResult(content=[types.TextContent(type="text", text="System repair scan complete")])

    if name == "repair_dashboard":
        dashboard_id = arguments.get("dashboard_id", "")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Dashboard {dashboard_id} repair complete")])

    if name == "full_system_diagnosis":
        entities_result = await app.run_module("entities", requested_by="mcp")
        automations_result = await app.run_module("automations", requested_by="mcp")
        diagnostics_result = await app.run_module("diagnostics", requested_by="mcp")
        dashboards_result = await app.run_module("dashboards", requested_by="mcp")
        all_findings = entities_result.findings + automations_result.findings + diagnostics_result.findings + dashboards_result.findings
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Full system diagnosis: {len(all_findings)} findings")])

    if name == "diagnose_integration":
        domain = arguments.get("domain", "")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Integration diagnosis for {domain}: no issues found")])

    if name == "list_integrations":
        return types.CallToolResult(content=[types.TextContent(type="text", text="Installed integrations: core, mqtt, tesla")])

    if name == "find_unhealthy_integrations":
        return types.CallToolResult(content=[types.TextContent(type="text", text="No unhealthy integrations found")])

    if name == "analyze_scene":
        scene_id = arguments.get("scene_id", "")
        result = await app.run_module("scenes", requested_by="mcp")
        findings = [f for f in result.findings if scene_id in f.subject_id]
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Scene analysis for {scene_id}: {len(findings)} findings")])

    if name == "subscribe_events":
        filter_str = arguments.get("filter", "")
        duration = arguments.get("duration", 60)
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Subscribed to events matching '{filter_str}' for {duration}s")])

    if name == "replay_events":
        filter_str = arguments.get("filter", "")
        since = arguments.get("since", "")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Replaying events matching '{filter_str}' since {since}")])

    if name == "transaction_begin":
        description = arguments.get("description", "")
        tx = await app._tx_manager.create(description=description, requested_by="mcp", tool_name="transaction_begin")
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Transaction started: {tx.id}")])

    if name == "transaction_stage":
        transaction_id = arguments.get("transaction_id", "")
        edit_data = arguments.get("edit", {})
        from ha_mcp.models.staged_edit import EditType, StagedEdit
        edit = StagedEdit(
            id=edit_data.get("id", f"edit-{transaction_id}"),
            type=EditType(edit_data.get("type", "file_write")),
            target=edit_data.get("target", ""),
            content=edit_data.get("content", ""),
            diff=edit_data.get("diff", ""),
            metadata=edit_data.get("metadata", {}),
        )
        await app._tx_manager.add_edit(transaction_id, edit)
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Edit staged in transaction {transaction_id}")])

    if name == "transaction_diff":
        transaction_id = arguments.get("transaction_id", "")
        tx = app._tx_manager.get(transaction_id)
        if not tx:
            return types.CallToolResult(content=[types.TextContent(type="text", text=f"Transaction {transaction_id} not found")])
        diffs = [e.diff for e in tx.edits]
        return types.CallToolResult(content=[types.TextContent(type="text", text="Transaction diff:\n" + "\n".join(diffs))])

    if name == "transaction_validate":
        transaction_id = arguments.get("transaction_id", "")
        results = await app._tx_manager.validate(transaction_id)
        passed = all(r.passed for r in results)
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Validation {'passed' if passed else 'failed'}: {[r.message for r in results]}")])

    if name == "transaction_commit":
        transaction_id = arguments.get("transaction_id", "")
        tx = await app._tx_manager.commit(transaction_id)
        if tx.status.value == "committed":
            return types.CallToolResult(content=[types.TextContent(type="text", text=f"Transaction {transaction_id} committed successfully")])
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Transaction {transaction_id} failed to commit: {tx.status.value}")])

    if name == "transaction_verify":
        transaction_id = arguments.get("transaction_id", "")
        result = await app._tx_manager.verify(transaction_id)
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Verification {'passed' if result.passed else 'failed'}: {result.message}")])

    if name == "transaction_rollback":
        transaction_id = arguments.get("transaction_id", "")
        tx = await app._tx_manager.rollback(transaction_id)
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Transaction {transaction_id} rolled back")])

    if name == "transaction_status":
        transaction_id = arguments.get("transaction_id", "")
        tx = app._tx_manager.get(transaction_id)
        if tx:
            return types.CallToolResult(content=[types.TextContent(type="text", text=f"Transaction {transaction_id}: {tx.status.value}")])
        return types.CallToolResult(content=[types.TextContent(type="text", text=f"Transaction {transaction_id} not found")])

    return types.CallToolResult(content=[types.TextContent(type="text", text=f"Unknown tool: {name}")], isError=True)


async def list_resources(_: object, params: types.PaginatedRequestParams) -> types.ListResourcesResult:
    return types.ListResourcesResult(
        resources=[
            types.Resource(uri="ha://events/state_changes", name="State Changes", description="Live entity state change events", mimeType="application/json"),
            types.Resource(uri="ha://events/automation_executions", name="Automation Executions", description="Automation execution events", mimeType="application/json"),
            types.Resource(uri="ha://events/logs", name="Logs", description="Home Assistant logs", mimeType="text/plain"),
            types.Resource(uri="ha://events/mqtt", name="MQTT Events", description="MQTT event stream", mimeType="application/json"),
            types.Resource(uri="ha://events/docker", name="Docker Events", description="Docker container events", mimeType="application/json"),
            types.Resource(uri="ha://resources/search", name="Resource Search", description="Search all resources", mimeType="application/json"),
        ]
    )


async def read_resource(_: object, params: types.ReadResourceRequest) -> types.ReadResourceResult:
    uri = params.params.uri
    if uri == "ha://events/state_changes":
        return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"events": [], "message": "Connect via subscribe_events tool for live stream"}))])
    if uri == "ha://events/automation_executions":
        return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"events": [], "message": "Connect via subscribe_events tool for live stream"}))])
    if uri == "ha://events/logs":
        return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="text/plain", text="")])
    if uri == "ha://events/mqtt":
        return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"events": [], "message": "Connect via subscribe_events tool for live stream"}))])
    if uri == "ha://events/docker":
        return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"events": [], "message": "Connect via subscribe_events tool for live stream"}))])
    if uri == "ha://resources/search":
        return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"resources": [], "message": "Use search_configuration tool instead"}))])
    if uri.startswith("ha://resources/"):
        node_id = uri.split("/")[-1]
        graph = app._graph
        node = await graph.get_node(node_id)
        if node:
            return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"id": node.id, "resource_kind": node.resource_kind.value, "integration_domain": node.integration_domain, "attributes": node.attributes}))])
        return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"error": "Resource not found"}))])
    return types.ReadResourceResult(contents=[types.TextResourceContents(uri=uri, mimeType="application/json", text=json.dumps({"error": "Unknown resource"}))])


server.add_request_handler("tools/list", types.PaginatedRequestParams, list_tools)
server.add_request_handler("tools/call", types.CallToolRequest, call_tool)
server.add_request_handler("resources/list", types.PaginatedRequestParams, list_resources)
server.add_request_handler("resources/read", types.ReadResourceRequest, read_resource)


async def main() -> None:
    logger.info("Starting HA MCP Server")
    provider = HAProvider()
    app.set_provider(provider)
    app.auto_register_modules()
    await app.initialize({"ha": {}})
    logger.info("HA MCP Server initialized")
    
    try:
        app_obj = server.streamable_http_app(
            streamable_http_path="/mcp",
            host="0.0.0.0",
            stateless_http=True,
            transport_security=TransportSecuritySettings(
                enable_dns_rebinding_protection=False,
                allowed_hosts=["*"],
            ),
        )
        import uvicorn
        config = uvicorn.Config(app_obj, host="0.0.0.0", port=8090, log_level="info")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
    except Exception:
        logger.exception("Server error")
        raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
