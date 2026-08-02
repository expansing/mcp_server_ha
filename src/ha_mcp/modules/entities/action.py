from __future__ import annotations

from typing import Any

from ha_mcp.models.action import Action
from ha_mcp.models.recommendation import Recommendation
from ha_mcp.models.staged_edit import EditType, StagedEdit


class NotifyAction(Action):
    async def compile(
        self, recommendation: Recommendation, context: dict[str, Any]
    ) -> list[StagedEdit]:
        return [
            StagedEdit(
                id=f"notify-{recommendation.finding_id}",
                type=EditType.SERVICE_CALL,
                target="notify",
                content={
                    "service": "persistent_notification",
                    "domain": "notify",
                    "data": {
                        "message": recommendation.description or "Action required",
                        "title": recommendation.title or "Recommendation",
                    },
                },
                diff=f"Call notify.persistent_notification for finding {recommendation.finding_id}",
                metadata={"finding_id": recommendation.finding_id},
            )
        ]
