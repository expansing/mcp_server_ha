from __future__ import annotations

from typing import Any

from ha_mcp.models.action import Action
from ha_mcp.models.recommendation import Recommendation
from ha_mcp.models.staged_edit import EditType, StagedEdit


class FixDashboardAction(Action):
    async def compile(
        self, recommendation: Recommendation, context: dict[str, Any]
    ) -> list[StagedEdit]:
        return [
            StagedEdit(
                id=f"fix-dashboard-{recommendation.finding_id}",
                type=EditType.SERVICE_CALL,
                target="dashboard",
                content={"dashboard_id": context.get("dashboard_id")},
                diff=f"Review and fix dashboard {context.get('dashboard_id')}",
                metadata={"finding_id": recommendation.finding_id},
            )
        ]
