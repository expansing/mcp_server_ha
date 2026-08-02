from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Capability, Provider


class MinimalProvider:
    name: str = "test"
    capabilities: frozenset[Capability] = frozenset([Capability.READ])

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> Observation:
        return Observation(
            id="obs1",
            type=ObservationType.STATE,
            subject_id=resource_id,
            timestamp=__import__("datetime").datetime.now(),
            data={},
            source=self.name,
        )

    async def write(self, resource_id: str, content: Any) -> None:
        pass

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        return None

    async def subscribe(self, filter: dict[str, Any], callback: Callable) -> None:
        pass


class TestProviderProtocol:
    def test_minimal_provider_conforms(self):
        provider = MinimalProvider()
        assert isinstance(provider, Provider)

    def test_capabilities_are_frozenset(self):
        assert isinstance(MinimalProvider.capabilities, frozenset)

    def test_missing_capabilities_breaks_compliance(self):
        class BrokenProvider:
            name: str = "broken"

        broken = BrokenProvider()
        assert not isinstance(broken, Provider)
