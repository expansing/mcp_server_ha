from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.graph.graph_repository import GraphRepository


class EventsAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.EVENT:
                continue
            event_type = obs.data.get("event_type", "")
            if event_type == "error":
                findings.append(
                    Finding(
                        id=f"event-error-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="event_error",
                        message=f"Error event detected: {obs.data.get('message', '')}",
                        severity=Severity.ERROR,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"event_type": event_type},
                    )
                )
        return findings
