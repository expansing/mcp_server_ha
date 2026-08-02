#!/bin/bash
set -e

CONFIG_PATH="/data/options.json"

HA_URL="$(jq --raw-output '.ha_url' "$CONFIG_PATH")"
HA_TOKEN="$(jq --raw-output '.ha_token' "$CONFIG_PATH")"
HA_VERIFY_SSL="$(jq --raw-output '.ha_verify_ssl' "$CONFIG_PATH")"

if [ "$HA_URL" = "http://homeassistant:8123" ]; then
    HA_URL="http://supervisor/core"
fi

if [ "$HA_URL" = "http://supervisor/core" ] && [ -n "${SUPERVISOR_TOKEN:-}" ]; then
    HA_TOKEN="$SUPERVISOR_TOKEN"
fi

if [ -z "$HA_TOKEN" ]; then
    echo "Error: a Home Assistant token is required" >&2
    exit 1
fi

export HA_URL
export HA_TOKEN
export HA_VERIFY_SSL

echo "Starting HA MCP Server..." >&2
echo "HA_URL=$HA_URL" >&2
echo "HA_VERIFY_SSL=$HA_VERIFY_SSL" >&2

cd /app
exec /app/venv/bin/python -m ha_mcp.server
