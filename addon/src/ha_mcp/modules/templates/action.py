from __future__ import annotations

from typing import Any

from ha_mcp.models.action import Action
from ha_mcp.models.recommendation import Recommendation
from ha_mcp.models.staged_edit import EditType, StagedEdit


class FixTemplateAction(Action):
    async def compile(
        self, recommendation: Recommendation, context: dict[str, Any]
    ) -> list[StagedEdit]:
        return [
            StagedEdit(
                id=f"fix-template-{recommendation.finding_id}",
                type=EditType.FILE_WRITE,
                target=context.get("template_path", ""),
                content="",
                diff=f"Review and fix template {context.get('entity_id', '')}",
                metadata={"finding_id": recommendation.finding_id},
            )
        ]
