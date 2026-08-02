from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DetectionManifest:
    ha_integrations: list[str] = field(default_factory=list)
    entities_pattern: list[str] = field(default_factory=list)
    addons: list[str] = field(default_factory=list)
    filesystem_paths: list[str] = field(default_factory=list)
    docker_containers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    detection: DetectionManifest
    target_domains: list[str] = field(default_factory=list)
    required_providers: list[str] = field(default_factory=list)
