from __future__ import annotations

from typing import Any

from ha_mcp.models.action import Action
from ha_mcp.models.recommendation import Recommendation
from ha_mcp.models.staged_edit import EditType, StagedEdit


class IntegrationGenericAction(Action):
    async def compile(self, recommendation: Recommendation, context: dict[str, Any]) -> list[StagedEdit]:
        return [
            StagedEdit(
                id=f"integration-action-{recommendation.finding_id}",
                type=EditType.SERVICE_CALL,
                target="integration",
                content={"domain": context.get("domain", "")},
                diff=f"Review integration {context.get('domain', '')}",
                metadata={"finding_id": recommendation.finding_id},
            )
        ]
