#!/bin/bash

set -e

CONFIG_PATH="/data/options.json"

HA_URL="$(jq --raw-output '.ha_url' "$CONFIG_PATH")"
HA_TOKEN="$(jq --raw-output '.ha_token' "$CONFIG_PATH")"
HA_VERIFY_SSL="$(jq --raw-output '.ha_verify_ssl' "$CONFIG_PATH")"

if [ -z "$HA_TOKEN" ]; then
    echo "Error: HA_TOKEN is required"
    exit 1
fi

export HA_URL
export HA_TOKEN
export HA_VERIFY_SSL

/app/venv/bin/python -m ha_mcp.server
