from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType


class ScenesAnalyzer:
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            entities = obs.data.get("entities", {})
            if not entities:
                findings.append(
                    Finding(
                        id=f"empty-scene-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="empty_scene",
                        message=f"Scene {obs.subject_id} ({obs.data.get('name', '')}) has no entities.",
                        severity=Severity.INFO,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"entity_id": obs.subject_id},
                    )
                )
        return findings
