from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Callable

import aiohttp

from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Capability, Provider
from ha_mcp.models.graph_node import GraphNode, ResourceKind


class HAProvider:
    name = "ha"
    capabilities = frozenset(
        {
            Capability.DISCOVER,
            Capability.READ,
            Capability.WRITE,
            Capability.EXECUTE,
            Capability.STREAM,
        }
    )

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._config: dict[str, Any] = {}
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._ws_task: asyncio.Task | None = None

    async def initialize(self, config: dict[str, Any]) -> None:
        self._config = config
        url = config.get("url", "http://homeassistant.local:8123")
        token = config.get("token", "")
        verify_ssl = config.get("verify_ssl", True)
        connector = aiohttp.TCPConnector(ssl=verify_ssl)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        self._session = aiohttp.ClientSession(base_url=url, headers=headers, connector=connector)

    async def shutdown(self) -> None:
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
            self._ws_task = None
        if self._ws and not self._ws.closed:
            await self._ws.close()
            self._ws = None
        if self._session:
            await self._session.close()
            self._session = None

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> Observation:
        raise NotImplementedError("HAProvider.read not implemented")

    async def write(self, resource_id: str, content: Any) -> None:
        raise NotImplementedError("HAProvider.write not implemented")

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("HAProvider.execute not implemented")

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        if not self._session:
            raise RuntimeError("HAProvider not initialized")
        async with self._session.request(method, path, **kwargs) as resp:
            resp.raise_for_status()
            if resp.status == 204:
                return None
            return await resp.json()

    async def get_states(self) -> list[Observation]:
        states = await self._request("GET", "/api/states")
        return [self._entity_dict_to_observation(e) for e in states]

    async def get_entity_registry(self) -> list[GraphNode]:
        entries = await self._request("GET", "/api/config/entity_registry/list")
        return [self._entity_dict_to_graph_node(e) for e in entries]

    async def get_automations(self) -> list[dict[str, Any]]:
        entries = await self._request("GET", "/api/config/automation/config")
        return entries if isinstance(entries, list) else []

    async def get_scenes(self) -> list[dict[str, Any]]:
        entries = await self._request("GET", "/api/scene")
        return entries if isinstance(entries, list) else []

    async def get_dashboards(self) -> list[dict[str, Any]]:
        entries = await self._request("GET", "/api/dashboards")
        return entries if isinstance(entries, list) else []

    async def get_templates(self) -> list[dict[str, Any]]:
        entries = await self._request("GET", "/api/template")
        return entries if isinstance(entries, list) else []

    async def call_service(self, domain: str, service: str, data: dict[str, Any]) -> None:
        await self._request("POST", f"/api/services/{domain}/{service}", json=data)

    async def subscribe(self, filter: dict[str, Any], callback: Callable) -> None:
        if not self._session:
            raise RuntimeError("HAProvider not initialized")
        ws_url = self._config.get("url", "http://homeassistant.local:8123").replace("http", "ws")
        ws = await self._session.ws_connect(f"{ws_url}/api/websocket")
        self._ws = ws
        auth_required = await ws.receive_json()
        if auth_required.get("type") == "auth_required":
            await ws.send_json(
                {
                    "type": "auth",
                    "access_token": self._config.get("token", ""),
                }
            )
            auth_result = await ws.receive_json()
            if auth_result.get("type") != "auth_ok":
                raise RuntimeError(f"HA WebSocket auth failed: {auth_result}")

        event_types = filter.get("event_types", [])
        if event_types:
            await ws.send_json({"id": 1, "type": "subscribe_events", "event_type": event_types})
        else:
            await ws.send_json({"id": 1, "type": "subscribe_events"})

        async def _listen() -> None:
            try:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        event = msg.json()
                        if event.get("type") == "event":
                            callback(event.get("data", {}))
            except asyncio.CancelledError:
                pass

        self._ws_task = asyncio.create_task(_listen())

    def _entity_dict_to_observation(self, entity_dict: dict[str, Any]) -> Observation:
        return Observation(
            id=entity_dict["entity_id"],
            type=ObservationType.STATE,
            subject_id=entity_dict["entity_id"],
            timestamp=datetime.fromisoformat(entity_dict.get("last_changed", datetime.now().isoformat())),
            data={
                "state": entity_dict.get("state"),
                "attributes": entity_dict.get("attributes", {}),
                "last_changed": entity_dict.get("last_changed"),
                "last_updated": entity_dict.get("last_updated"),
            },
            source="ha",
        )

    def _entity_dict_to_graph_node(self, entity_dict: dict[str, Any]) -> GraphNode:
        entity_id = entity_dict.get("entity_id", "")
        config_entry_id = entity_dict.get("config_entry_id")
        return GraphNode(
            id=entity_id,
            resource_kind=ResourceKind.ENTITY,
            integration_domain=config_entry_id,
            attributes={
                "name": entity_dict.get("name"),
                "original_name": entity_dict.get("original_name"),
                "entity_id": entity_id,
                "config_entry_id": config_entry_id,
                "disabled": entity_dict.get("disabled", False),
                "platform": entity_dict.get("platform"),
            },
        )

    async def get_events(self) -> list[dict[str, Any]]:
        return []

    async def get_scripts(self) -> list[dict[str, Any]]:
        entries = await self._request("GET", "/api/config/script")
        return entries if isinstance(entries, list) else []
