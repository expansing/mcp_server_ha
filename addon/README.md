# HA MCP Server

AI sysadmin for Home Assistant. This app exposes diagnostics, automation health, entity monitoring, dashboard analysis, and configuration search via the Model Context Protocol (MCP).

## Configuration

- **HA_URL**: Home Assistant URL (default: `http://homeassistant:8123`)
- **HA_TOKEN**: Long-lived access token (required)
- **HA_VERIFY_SSL**: Verify SSL certificates (default: `false`)

## Usage

This app runs as a service and provides an MCP interface over stdio. Connect to it using any MCP-compatible client.
