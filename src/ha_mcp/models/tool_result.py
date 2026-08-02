from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ha_mcp.models.finding import Finding
from ha_mcp.models.recommendation import Recommendation


@dataclass
class ToolResult:
    status: str
    summary: str
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    transaction_id: str | None = None
