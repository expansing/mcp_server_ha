from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ha_mcp.models.recommendation import Recommendation
from ha_mcp.models.staged_edit import StagedEdit


class Action(ABC):
    @abstractmethod
    async def compile(
        self, recommendation: Recommendation, context: dict[str, Any]
    ) -> list[StagedEdit]:
        pass
