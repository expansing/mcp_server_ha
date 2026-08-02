from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from ha_mcp.app import App
from ha_mcp.models.graph_node import GraphNode
from ha_mcp.modules.entities.module import EntitiesModule
from ha_mcp.providers.base import ProviderRegistry


class FakeGraphRepo:
    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}

    async def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    async def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        return []

    async def find(self, query: dict[str, Any]) -> list[GraphNode]:
        return list(self._nodes.values())

    async def search(self, text: str) -> list[GraphNode]:
        return []

    async def update(self, node: GraphNode) -> None:
        self._nodes[node.id] = node

    async def remove(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)


class FakeHAForApp:
    name = "ha"
    capabilities = frozenset()

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def get_states(self) -> list[dict[str, Any]]:
        return [
            {
                "entity_id": "sensor.stale",
                "state": "unavailable",
                "attributes": {},
                "last_changed": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
            }
        ]


class TestApp:
    @pytest.mark.asyncio
    async def test_direct_provider_is_initialized_and_shutdown(self):
        app = App()
        provider = MagicMock()
        provider.name = "ha"
        provider.initialize = AsyncMock()
        provider.shutdown = AsyncMock()
        app.set_provider(provider)

        await app.initialize({"ha": {"token": "test-token"}})
        await app.shutdown()

        provider.initialize.assert_awaited_once_with({"token": "test-token"})
        provider.shutdown.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_run_module_returns_findings(self):
        app = App()
        provider = FakeHAForApp()
        registry = ProviderRegistry()
        registry.register(provider)
        app.set_registry(registry)
        module = EntitiesModule(provider)
        app.register_module("entities", module)
        await app.initialize({"ha": {}})
        result = await app.run_module("entities", requested_by="test")
        assert result.status == "success"
        categories = {f.category for f in result.findings}
        assert "stale_entity" in categories
        await app.shutdown()

    @pytest.mark.asyncio
    async def test_run_missing_module_returns_error(self):
        app = App()
        result = await app.run_module("nonexistent", requested_by="test")
        assert result.status == "error"
        assert "not found" in result.summary

    @pytest.mark.asyncio
    async def test_run_module_handles_exception(self):
        app = App()
        broken_module = MagicMock()
        broken_module.run = AsyncMock(side_effect=RuntimeError("boom"))
        app.register_module("broken", broken_module)
        result = await app.run_module("broken", requested_by="test")
        assert result.status == "error"
        assert "boom" in result.details["error"]
