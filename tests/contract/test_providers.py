from __future__ import annotations

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


@pytest.mark.parametrize(
    "provider_class,expected_capabilities",
    [
        (HAProvider, {Capability.DISCOVER, Capability.READ, Capability.WRITE, Capability.EXECUTE, Capability.STREAM}),
        (GitProvider, {Capability.DISCOVER, Capability.READ, Capability.WRITE}),
        (FilesystemProvider, {Capability.READ, Capability.WRITE}),
        (DockerProvider, {Capability.DISCOVER, Capability.READ, Capability.EXECUTE, Capability.STREAM}),
        (MQTTProvider, {Capability.DISCOVER, Capability.READ, Capability.WRITE, Capability.STREAM}),
        (LogsProvider, {Capability.READ, Capability.STREAM}),
        (EventsProvider, {Capability.STREAM}),
    ],
)
def test_provider_contract(provider_class, expected_capabilities):
    provider = provider_class()
    assert isinstance(provider, Provider)
    assert isinstance(provider.capabilities, frozenset)
    assert provider.capabilities == expected_capabilities


@pytest.mark.parametrize(
    "provider_class",
    [HAProvider, GitProvider, FilesystemProvider, DockerProvider, MQTTProvider, LogsProvider, EventsProvider],
)
def test_provider_has_name(provider_class):
    provider = provider_class()
    assert isinstance(provider.name, str)
    assert len(provider.name) > 0


@pytest.mark.parametrize(
    "provider_class",
    [HAProvider, GitProvider, FilesystemProvider, DockerProvider, MQTTProvider, LogsProvider, EventsProvider],
)
@pytest.mark.asyncio
async def test_provider_initialize_and_shutdown(provider_class):
    provider = provider_class()
    await provider.initialize({})
    await provider.shutdown()


def test_provider_registry_register_and_get():
    registry = ProviderRegistry()
    registry.register(HAProvider())
    assert registry.get("ha").name == "ha"


def test_provider_registry_get_missing_raises():
    registry = ProviderRegistry()
    with pytest.raises(KeyError):
        registry.get("nonexistent")
