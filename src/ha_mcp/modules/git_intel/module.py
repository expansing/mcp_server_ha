from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer, Collector
from ha_mcp.models.finding import Finding
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository


class GitIntelCollector:
    def __init__(self, git_provider: Provider) -> None:
        self._git = git_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            status = await self._git.status()
        except Exception:
            status = {}
        observations.append(
            Observation(
                id="git-intel-status",
                type=ObservationType.STATE,
                subject_id="git",
                timestamp=__import__("datetime").datetime.now(),
                data=status,
                source="git",
            )
        )
        return observations


class GitIntelAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            data = obs.data
            if data.get("error"):
                findings.append(
                    Finding(
                        id="git-intel-error",
                        subject_id="git",
                        category="git_error",
                        message=f"Git error: {data.get('error')}",
                        severity=__import__("ha_mcp.models.finding").Severity.ERROR,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata=data,
                    )
                )
        return findings


class GitIntelModule:
    def __init__(self, git_provider: Provider) -> None:
        self._collector = GitIntelCollector(git_provider)
        self._analyzer = GitIntelAnalyzer()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
