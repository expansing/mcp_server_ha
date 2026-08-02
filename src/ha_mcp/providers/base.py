from __future__ import annotations

from typing import Any

from ha_mcp.models.provider_protocol import Provider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, Provider] = {}

    def register(self, provider: Provider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> Provider:
        try:
            return self._providers[name]
        except KeyError:
            raise KeyError(f"Provider '{name}' not found. Available: {list(self._providers)}")

    async def initialize_all(self, config: dict[str, Any]) -> None:
        for provider in self._providers.values():
            await provider.initialize(config.get(provider.name, {}))

    async def shutdown_all(self) -> None:
        for provider in reversed(list(self._providers.values())):
            await provider.shutdown()
