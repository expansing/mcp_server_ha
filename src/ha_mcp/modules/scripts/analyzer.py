from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.graph.graph_repository import GraphRepository


class ScriptsAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            if not obs.data.get("sequence"):
                findings.append(
                    Finding(
                        id=f"empty-script-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="empty_script",
                        message=f"Script {obs.subject_id} has no sequence.",
                        severity=Severity.INFO,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"entity_id": obs.subject_id},
                    )
                )
        return findings
