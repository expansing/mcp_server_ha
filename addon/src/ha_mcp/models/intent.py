from __future__ import annotations

from enum import Enum


class Intent(str, Enum):
    INSPECT = "inspect"
    VALIDATE = "validate"
    DIAGNOSE = "diagnose"
    EXPLAIN = "explain"
    OPTIMIZE = "optimize"
    REPAIR = "repair"
    SIMULATE = "simulate"
