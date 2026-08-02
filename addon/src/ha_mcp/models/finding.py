from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Finding:
    id: str
    subject_id: str
    category: str
    message: str
    severity: Severity
    evidence: tuple[str, ...] = ()
    confidence: float = 1.0
    schema_version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)
