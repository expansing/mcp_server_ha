from __future__ import annotations

from typing import Any
from datetime import datetime

from ha_mcp.analysis.pipeline import Analyzer, Collector
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository


class DockerHealthCollector:
    def __init__(self, docker_provider: Provider) -> None:
        self._docker = docker_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            containers = await self._docker.list_containers()
        except Exception:
            containers = []
        for container in containers:
            name = container.get("name", "")
            observations.append(
                Observation(
                    id=f"docker-{name}",
                    type=ObservationType.STATE,
                    subject_id=name,
                    timestamp=datetime.now(),
                    data=container,
                    source="docker",
                )
            )
        return observations


class DockerHealthAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            status = obs.data.get("status", "")
            if status not in ("running", "healthy"):
                findings.append(
                    Finding(
                        id=f"docker-unhealthy-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="docker_health",
                        message=f"Container {obs.subject_id} is {status}",
                        severity=Severity.WARNING,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"container": obs.subject_id, "status": status},
                    )
                )
        return findings


class DockerHealthModule:
    def __init__(self, docker_provider: Provider) -> None:
        self._collector = DockerHealthCollector(docker_provider)
        self._analyzer = DockerHealthAnalyzer()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
