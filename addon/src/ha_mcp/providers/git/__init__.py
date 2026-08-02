from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from ha_mcp.models.provider_protocol import Capability, Provider


class GitProvider:
    name = "git"
    capabilities = frozenset({Capability.DISCOVER, Capability.READ, Capability.WRITE})

    def __init__(self) -> None:
        self._repo_path: str = ""
        self._repo: Any = None

    async def initialize(self, config: dict[str, Any]) -> None:
        self._repo_path = config.get("repo_path", "/config")
        try:
            from dulwich import porcelain

            self._repo = porcelain.open_repo(self._repo_path)
        except Exception:
            self._repo = None

    async def shutdown(self) -> None:
        self._repo = None

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> str:
        return await self.read_file(resource_id)

    async def write(self, resource_id: str, content: Any) -> None:
        await self.write_file(resource_id, content)

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("GitProvider.execute not implemented")

    async def subscribe(self, filter: dict[str, Any], callback: Any) -> None:
        raise NotImplementedError("GitProvider.subscribe not implemented")

    async def status(self) -> dict[str, Any]:
        if not self._repo:
            return {"error": "repo not open"}
        from dulwich import porcelain

        return porcelain.status(self._repo)

    async def diff(self, path: str) -> str:
        if not self._repo:
            return ""
        from dulwich import porcelain

        try:
            diff = porcelain.diff(self._repo, path)
            return diff.decode("utf-8", errors="replace") if isinstance(diff, bytes) else str(diff)
        except Exception:
            return ""

    async def read_file(self, path: str) -> str:
        full_path = path if path.startswith("/") else f"{self._repo_path}/{path}"
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    async def write_file(self, path: str, content: str) -> None:
        full_path = path if path.startswith("/") else f"{self._repo_path}/{path}"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
