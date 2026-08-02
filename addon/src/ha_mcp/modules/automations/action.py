from __future__ import annotations

from typing import Any

from ha_mcp.models.action import Action
from ha_mcp.models.recommendation import Recommendation
from ha_mcp.models.staged_edit import EditType, StagedEdit


class EnableAutomationAction(Action):
    async def compile(
        self, recommendation: Recommendation, context: dict[str, Any]
    ) -> list[StagedEdit]:
        return [
            StagedEdit(
                id=f"enable-automation-{recommendation.finding_id}",
                type=EditType.SERVICE_CALL,
                target="automation",
                content={"service": "turn_on", "entity_id": context.get("entity_id")},
                diff=f"Enable automation {context.get('entity_id')}",
                metadata={"finding_id": recommendation.finding_id},
            )
        ]
