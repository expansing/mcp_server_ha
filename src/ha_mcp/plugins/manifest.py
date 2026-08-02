from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PluginManifest:
    name: str
    version: str
    description: str
    author: str
    capabilities: frozenset[str]
    dependencies: tuple[str, ...] = ()
    entry_point: str = ""
