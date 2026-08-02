from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class Effort(str, Enum):
    TRIVIAL = "trivial"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"


class Risk(str, Enum):
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class Recommendation:
    id: str
    finding_ids: tuple[str, ...]
    action: str
    rationale: str
    effort: Effort
    risk: Risk
    priority: Literal["high", "medium", "low"]
    automatable: bool
