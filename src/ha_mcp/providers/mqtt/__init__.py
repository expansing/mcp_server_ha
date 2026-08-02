from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ha_mcp.models.provider_protocol import Capability
from ha_mcp.models.provider_protocol import Provider as Provider


class MQTTProvider:
    name = "mqtt"
    capabilities = frozenset({Capability.DISCOVER, Capability.READ, Capability.WRITE, Capability.STREAM})

    def __init__(self) -> None:
        self._broker: str = ""
        self._client: Any = None

    async def initialize(self, config: dict[str, Any]) -> None:
        self._broker = config.get("broker", "mqtt://homeassistant.local:1883")
        try:
            import aiomqtt

            self._client = aiomqtt.Client(self._broker)
        except Exception:
            self._client = None

    async def shutdown(self) -> None:
        if self._client:
            try:
                await self._client.__aexit__(None, None, None)
            except Exception:
                pass
            self._client = None

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> str:
        raise NotImplementedError("MQTTProvider.read not implemented")

    async def write(self, resource_id: str, content: Any) -> None:
        raise NotImplementedError("MQTTProvider.write not implemented")

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("MQTTProvider.execute not implemented")

    async def publish(self, topic: str, payload: str) -> None:
        if not self._client:
            raise RuntimeError("MQTTProvider not initialized")
        async with self._client as client:
            await client.publish(topic, payload)

    async def subscribe(self, topic: str, callback: Callable) -> None:
        if not self._client:
            raise RuntimeError("MQTTProvider not initialized")
        async with self._client as client, client.messages(topic) as messages:
            async for message in messages:
                callback(message.payload.decode("utf-8", errors="replace"))
