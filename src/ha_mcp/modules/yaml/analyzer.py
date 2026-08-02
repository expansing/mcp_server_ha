from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.graph.graph_repository import GraphRepository


class YAMLAnalyzer:
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            content = obs.data.get("content", "")
            if not content.strip():
                findings.append(
                    Finding(
                        id="empty-yaml",
                        subject_id=obs.subject_id,
                        category="empty_yaml",
                        message=f"YAML file '{obs.subject_id}' is empty.",
                        severity=Severity.WARNING,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"path": obs.data.get("path")},
                    )
                )
        return findings
