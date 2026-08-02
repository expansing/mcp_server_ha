from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ObservationType(str, Enum):
    STATE = "state"
    LOG = "log"
    METRIC = "metric"
    TRACE = "trace"
    HISTORY = "history"
    EVENT = "event"


@dataclass(frozen=True)
class Observation:
    id: str
    type: ObservationType
    subject_id: str
    timestamp: datetime
    data: dict[str, Any]
    source: str
