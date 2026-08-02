from __future__ import annotations

from datetime import datetime
from typing import Any

from ha_mcp.models.provider_protocol import Capability, Provider


class DockerProvider:
    name = "docker"
    capabilities = frozenset({Capability.DISCOVER, Capability.READ, Capability.EXECUTE, Capability.STREAM})

    def __init__(self) -> None:
        self._socket: str = "/var/run/docker.sock"
        self._client: Any = None

    async def initialize(self, config: dict[str, Any]) -> None:
        self._socket = config.get("socket", "/var/run/docker.sock")
        try:
            import docker

            self._client = docker.DockerClient(base_url=f"unix://{self._socket}")
        except Exception:
            self._client = None

    async def shutdown(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> str:
        raise NotImplementedError("DockerProvider.read not implemented")

    async def write(self, resource_id: str, content: Any) -> None:
        raise NotImplementedError("DockerProvider.write not implemented")

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError("DockerProvider.execute not implemented")

    async def subscribe(self, filter: dict[str, Any], callback: Any) -> None:
        raise NotImplementedError("DockerProvider.subscribe not implemented")

    async def list_containers(self) -> list[dict[str, Any]]:
        if not self._client:
            return []
        return [
            {
                "id": c.id,
                "name": c.name,
                "status": c.status,
                "image": c.image.tags if c.image else [],
            }
            for c in self._client.containers.list(all=True)
        ]

    async def container_logs(self, name: str, since: datetime) -> list[str]:
        if not self._client:
            return []
        try:
            container = self._client.containers.get(name)
            logs = container.logs(since=since, stdout=True, stderr=True)
            return logs.decode("utf-8", errors="replace").splitlines()
        except Exception:
            return []

    async def restart_container(self, name: str) -> None:
        if not self._client:
            raise RuntimeError("DockerProvider not initialized")
        container = self._client.containers.get(name)
        container.restart()
