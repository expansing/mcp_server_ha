from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.graph.graph_repository import GraphRepository


class TemplatesAnalyzer:
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            content = obs.data.get("content", "")
            if "{{" not in content and "{%" not in content:
                findings.append(
                    Finding(
                        id=f"no-template-syntax-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="no_template_syntax",
                        message=f"Template '{obs.subject_id}' has no Jinja2 syntax.",
                        severity=Severity.INFO,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"entity_id": obs.subject_id},
                    )
                )
        return findings
