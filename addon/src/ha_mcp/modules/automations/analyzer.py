from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType


class AutomationsAnalyzer:
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            data = obs.data
            if not data.get("enabled", True):
                findings.append(
                    Finding(
                        id=f"disabled-automation-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="disabled_automation",
                        message=f"Automation {obs.subject_id} ({data.get('alias', '')}) is disabled.",
                        severity=Severity.INFO,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"entity_id": obs.subject_id},
                    )
                )
            if not data.get("trigger"):
                findings.append(
                    Finding(
                        id=f"no-trigger-automation-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="no_trigger",
                        message=f"Automation {obs.subject_id} has no triggers and will never run.",
                        severity=Severity.WARNING,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"entity_id": obs.subject_id},
                    )
                )
        return findings
