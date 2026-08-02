from __future__ import annotations

from datetime import UTC, datetime

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class BackupCollector:
    def __init__(self, filesystem_provider: Provider) -> None:
        self._fs = filesystem_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            contents = await self._fs.list("/backup")
        except Exception:
            contents = []
        for item in contents:
            observations.append(
                Observation(
                    id=f"backup-{item}",
                    type=ObservationType.STATE,
                    subject_id=item,
                    timestamp=datetime.now(tz=UTC),
                    data={"name": item, "path": f"/backup/{item}"},
                    source="filesystem",
                )
            )
        return observations


class BackupAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        if not observations:
            findings.append(
                Finding(
                    id="no-backups",
                    subject_id="backup",
                    category="no_backups",
                    message="No backups found in /backup",
                    severity=Severity.WARNING,
                    evidence=(),
                    confidence=1.0,
                    schema_version="1.0",
                    metadata={},
                )
            )
        return findings


class BackupModule:
    def __init__(self, filesystem_provider: Provider) -> None:
        self._collector = BackupCollector(filesystem_provider)
        self._analyzer = BackupAnalyzer()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
