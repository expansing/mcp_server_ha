from __future__ import annotations

import pytest
from ha_mcp.app import App
from ha_mcp.models.tool_result import ToolResult
from ha_mcp.modules.entities.module import EntitiesModule
from ha_mcp.providers.base import ProviderRegistry


class FakeHAProvider:
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
                "last_changed": (__import__("datetime").datetime.now() - __import__("datetime").timedelta(days=10)).isoformat(),
                "last_updated": (__import__("datetime").datetime.now() - __import__("datetime").timedelta(days=10)).isoformat(),
            }
        ]


class TestIntegration:
    @pytest.mark.asyncio
    async def test_full_pipeline_end_to_end(self):
        provider = FakeHAProvider()
        registry = ProviderRegistry()
        registry.register(provider)
        module = EntitiesModule(provider)
        app = App()
        app.set_registry(registry)
        app.register_module("entities", module)
        await app.initialize({"ha": {}})
        result = await app.run_module("entities", requested_by="integration-test")
        assert result.status == "success"
        categories = {f.category for f in result.findings}
        assert "stale_entity" in categories
        assert result.transaction_id is not None
        await app.shutdown()

    @pytest.mark.asyncio
    async def test_module_isolated_from_others(self):
        provider = FakeHAProvider()
        module = EntitiesModule(provider)
        registry = ProviderRegistry()
        registry.register(provider)
        app = App()
        app.set_registry(registry)
        app.register_module("entities", module)
        await app.initialize({"ha": {}})
        result = await app.run_module("entities", requested_by="test")
        assert result.status == "success"
        categories = {f.category for f in result.findings}
        assert "stale_entity" in categories
        await app.shutdown()
