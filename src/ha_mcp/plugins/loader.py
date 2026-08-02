from __future__ import annotations

import importlib.metadata
from typing import Any

from ha_mcp.plugins.manifest import PluginManifest


class PluginLoader:
    def __init__(self) -> None:
        self._plugins: dict[str, PluginManifest] = {}

    def discover_entry_points(self, group: str = "ha_mcp.plugins") -> list[PluginManifest]:
        plugins: list[PluginManifest] = []
        try:
            eps = importlib.metadata.entry_points(group=group)
            for ep in eps:
                try:
                    mod = importlib.import_module(ep.module)
                    manifest = getattr(mod, "manifest", None)
                    if isinstance(manifest, PluginManifest):
                        plugins.append(manifest)
                        self._plugins[manifest.name] = manifest
                except Exception:
                    continue
        except Exception:
            pass
        return plugins

    def load_plugin(self, name: str) -> Any:
        manifest = self._plugins.get(name)
        if not manifest:
            raise ValueError(f"Plugin '{name}' not found")
        return importlib.import_module(manifest.entry_point)

    def get_plugins(self) -> list[PluginManifest]:
        return list(self._plugins.values())
