from __future__ import annotations

from typing import Any

import aiohttp
import pytest

from ha_mcp.models.provider_protocol import Capability, Provider
from ha_mcp.providers.base import ProviderRegistry
from ha_mcp.providers.docker import DockerProvider
from ha_mcp.providers.events import EventsProvider
from ha_mcp.providers.filesystem import FilesystemProvider
from ha_mcp.providers.git import GitProvider
from ha_mcp.providers.ha import HAProvider
from ha_mcp.providers.logs import LogsProvider
from ha_mcp.providers.mqtt import MQTTProvider


class MinimalProvider:
    name = "minimal"
    capabilities = frozenset({Capability.READ})

    async def initialize(self, config: dict) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def discover(self) -> list[str]:
        return []

    async def read(self, resource_id: str) -> str:
        return ""

    async def write(self, resource_id: str, content: Any) -> None:
        pass

    async def execute(self, command: str, params: dict[str, Any]) -> Any:
        raise NotImplementedError()

    async def subscribe(self, filter: dict[str, Any], callback: Any) -> None:
        raise NotImplementedError()


class TestProviderProtocol:
    def test_minimal_provider_conforms(self):
        assert isinstance(MinimalProvider(), Provider)

    def test_capabilities_are_frozenset(self):
        assert isinstance(MinimalProvider.capabilities, frozenset)

    def test_missing_capabilities_breaks_compliance(self):
        class BadProvider:
            name = "bad"
            capabilities = "read"

        assert not isinstance(BadProvider(), Provider)


class TestProviderRegistry:
    def test_register_and_get(self):
        registry = ProviderRegistry()
        registry.register(MinimalProvider())
        assert registry.get("minimal").name == "minimal"

    def test_get_missing_raises(self):
        registry = ProviderRegistry()
        with pytest.raises(KeyError):
            registry.get("nonexistent")

    @pytest.mark.asyncio
    async def test_initialize_all(self):
        registry = ProviderRegistry()
        registry.register(MinimalProvider())
        await registry.initialize_all({"minimal": {"key": "value"}})

    @pytest.mark.asyncio
    async def test_shutdown_all(self):
        registry = ProviderRegistry()
        registry.register(MinimalProvider())
        await registry.shutdown_all()


class TestHAProvider:
    def test_name_and_capabilities(self):
        provider = HAProvider()
        assert provider.name == "ha"
        assert Capability.DISCOVER in provider.capabilities
        assert Capability.STREAM in provider.capabilities

    def test_conforms_to_protocol(self):
        assert isinstance(HAProvider(), Provider)

    @pytest.mark.asyncio
    async def test_initialize(self):
        provider = HAProvider()
        await provider.initialize({"url": "http://test:8123", "token": "tok", "verify_ssl": True})
        assert provider._session is not None
        await provider.shutdown()

    @pytest.mark.asyncio
    async def test_shutdown_without_init(self):
        provider = HAProvider()
        await provider.shutdown()

    @pytest.mark.asyncio
    async def test_request_error_identifies_home_assistant_endpoint(self):
        class FailingRequest:
            async def __aenter__(self):
                raise aiohttp.ServerDisconnectedError()

            async def __aexit__(self, exc_type, exc_value, traceback):
                return False

        class FailingSession:
            def request(self, *args, **kwargs):
                return FailingRequest()

        provider = HAProvider()
        provider._config = {"url": "http://homeassistant:8123"}
        provider._session = FailingSession()

        with pytest.raises(
            RuntimeError,
            match=r"GET http://homeassistant:8123/api/states failed: Server disconnected",
        ):
            await provider.get_states()


class TestGitProvider:
    def test_name_and_capabilities(self):
        provider = GitProvider()
        assert provider.name == "git"
        assert Capability.READ in provider.capabilities
        assert Capability.WRITE in provider.capabilities

    def test_conforms_to_protocol(self):
        assert isinstance(GitProvider(), Provider)

    @pytest.mark.asyncio
    async def test_initialize(self):
        provider = GitProvider()
        await provider.initialize({"repo_path": "/tmp"})
        assert provider._repo_path == "/tmp"

    @pytest.mark.asyncio
    async def test_read_write_file(self, tmp_path):
        provider = GitProvider()
        await provider.initialize({"repo_path": str(tmp_path)})
        test_file = tmp_path / "test.txt"
        await provider.write_file(str(test_file), "hello")
        content = await provider.read_file(str(test_file))
        assert content == "hello"


class TestFilesystemProvider:
    def test_name_and_capabilities(self):
        provider = FilesystemProvider()
        assert provider.name == "filesystem"
        assert Capability.READ in provider.capabilities
        assert Capability.WRITE in provider.capabilities

    def test_conforms_to_protocol(self):
        assert isinstance(FilesystemProvider(), Provider)

    @pytest.mark.asyncio
    async def test_read_write_exists(self, tmp_path):
        provider = FilesystemProvider()
        await provider.initialize({"base_path": str(tmp_path)})
        await provider.write("test.txt", "hello")
        assert await provider.exists("test.txt")
        content = await provider.read("test.txt")
        assert content == "hello"


class TestDockerProvider:
    def test_name_and_capabilities(self):
        provider = DockerProvider()
        assert provider.name == "docker"
        assert Capability.DISCOVER in provider.capabilities

    def test_conforms_to_protocol(self):
        assert isinstance(DockerProvider(), Provider)

    @pytest.mark.asyncio
    async def test_initialize(self):
        provider = DockerProvider()
        await provider.initialize({"socket": "/var/run/docker.sock"})
        assert provider._socket == "/var/run/docker.sock"


class TestMQTTProvider:
    def test_name_and_capabilities(self):
        provider = MQTTProvider()
        assert provider.name == "mqtt"
        assert Capability.STREAM in provider.capabilities

    def test_conforms_to_protocol(self):
        assert isinstance(MQTTProvider(), Provider)


class TestLogsProvider:
    def test_name_and_capabilities(self):
        provider = LogsProvider()
        assert provider.name == "logs"
        assert Capability.READ in provider.capabilities

    def test_conforms_to_protocol(self):
        assert isinstance(LogsProvider(), Provider)

    @pytest.mark.asyncio
    async def test_query_missing_file(self, tmp_path):
        provider = LogsProvider()
        await provider.initialize({"source": "file", "path": str(tmp_path / "missing.log")})
        results = await provider.query({})
        assert results == []


class TestEventsProvider:
    def test_name_and_capabilities(self):
        provider = EventsProvider()
        assert provider.name == "events"
        assert Capability.STREAM in provider.capabilities

    def test_conforms_to_protocol(self):
        assert isinstance(EventsProvider(), Provider)

    @pytest.mark.asyncio
    async def test_subscribe(self):
        provider = EventsProvider()
        await provider.initialize({"buffer_size": 100})
        received: list = []

        async def callback(event):
            received.append(event)

        await provider.subscribe({}, callback)
        await provider._emit({"type": "test", "data": "hello"})
        assert len(received) == 1
        assert received[0]["data"] == "hello"
