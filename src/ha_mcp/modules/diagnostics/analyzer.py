from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.graph.graph_repository import GraphRepository


class DiagnosticsAnalyzer:
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        entity_observations = [o for o in observations if o.type == ObservationType.STATE]
        if not entity_observations:
            return []

        total = len(entity_observations)
        critical = sum(1 for o in entity_observations if o.data.get("state") in ("unavailable", "unknown"))
        healthy = total - critical
        health_ratio = healthy / total if total else 1.0
        score = int(health_ratio * 100)

        if score >= 90:
            severity = Severity.INFO
        elif score >= 70:
            severity = Severity.WARNING
        else:
            severity = Severity.CRITICAL

        return [
            Finding(
                id="health-score",
                subject_id="system",
                category="health_score",
                message=f"System health score: {score}/100 ({healthy} healthy, {critical} issues out of {total} entities)",
                severity=severity,
                evidence=tuple(o.id for o in entity_observations[:10]),
                confidence=1.0,
                schema_version="1.0",
                metadata={
                    "score": score,
                    "total_entities": total,
                    "healthy": healthy,
                    "critical": critical,
                },
            )
        ]
