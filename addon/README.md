# HA MCP Server

AI sysadmin for Home Assistant. This app exposes diagnostics, automation health, entity monitoring, dashboard analysis, and configuration search via the Model Context Protocol (MCP).

## Configuration

 - **HA_URL**: Home Assistant API URL (default: `http://supervisor/core`)
 - **HA_TOKEN**: Long-lived access token when using a custom URL; the default Supervisor proxy uses the add-on's Supervisor token
- **HA_VERIFY_SSL**: Verify SSL certificates (default: `false`)

## Usage

This app runs a Streamable HTTP MCP server at `http://<home-assistant-host>:8090/mcp`.
Configure `ha_token` in the add-on configuration, then rebuild or restart the add-on
after changing its settings.
