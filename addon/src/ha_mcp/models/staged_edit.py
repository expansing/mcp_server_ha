from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EditType(str, Enum):
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    ENTITY_UPDATE = "entity_update"
    SERVICE_CALL = "service_call"


@dataclass(frozen=True)
class StagedEdit:
    id: str
    type: EditType
    target: str
    content: Any
    diff: str
    metadata: dict[str, Any] = field(default_factory=dict)
