from __future__ import annotations

import os
from typing import Any

from ha_mcp.models.provider_protocol import Capability, Provider


class FilesystemProvider:
    name = "filesystem"
    capabilities = frozenset({Capability.READ, Capability.WRITE})

    def __init__(self) -> None:
        self._base_path: str = ""

    async def initialize(self, config: dict[str, Any]) -> None:
        self._base_path = config.get("base_path", "/config")

    async def shutdown(self) -> None:
        pass

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> str:
        return await self.read_file(resource_id)

    async def write(self, resource_id: str, content: Any) -> None:
        await self.write_file(resource_id, content)

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("FilesystemProvider.execute not implemented")

    async def subscribe(self, filter: dict[str, Any], callback: Any) -> None:
        raise NotImplementedError("FilesystemProvider.subscribe not implemented")

    def _full_path(self, path: str) -> str:
        return os.path.normpath(os.path.join(self._base_path, path))

    async def read_file(self, path: str) -> str:
        full_path = self._full_path(path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    async def write_file(self, path: str, content: str) -> None:
        full_path = self._full_path(path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    async def exists(self, path: str) -> bool:
        return os.path.exists(self._full_path(path))

    async def list(self, path: str) -> list[str]:
        full_path = self._full_path(path)
        if not os.path.isdir(full_path):
            return []
        return os.listdir(full_path)
