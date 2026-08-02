from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ResourceKind(str, Enum):
    ENTITY = "entity"
    DEVICE = "device"
    WORKFLOW = "workflow"
    VISUALIZATION = "visualization"
    EXECUTION = "execution"
    CONFIGURATION = "configuration"
    TEMPLATE = "template"
    INTEGRATION = "integration"
    SERVICE = "service"


@dataclass(frozen=True)
class GraphNode:
    id: str
    resource_kind: ResourceKind
    integration_domain: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
