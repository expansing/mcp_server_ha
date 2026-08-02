from __future__ import annotations

from typing import Any

from ha_mcp.analysis.pipeline import Analyzer, Collector
from ha_mcp.models.finding import Finding
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider
from ha_mcp.graph.graph_repository import GraphRepository


class RepairCollector:
    def __init__(self, ha_provider: Provider) -> None:
        self._ha = ha_provider

    async def collect(self, graph: GraphRepository) -> list[Observation]:
        observations: list[Observation] = []
        try:
            states = await self._ha.get_states()
        except Exception:
            states = []
        for state in states:
            entity_id = state.get("entity_id", "")
            observations.append(
                Observation(
                    id=f"repair-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data=state,
                    source="ha",
                )
            )
        return observations


class RepairAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            state = obs.data.get("state", "")
            if state == "unavailable":
                findings.append(
                    Finding(
                        id=f"repair-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="repair_needed",
                        message=f"Entity {obs.subject_id} is unavailable and may need repair",
                        severity=__import__("ha_mcp.models.finding").Severity.WARNING,
                        evidence=(obs.id,),
                        confidence=0.8,
                        schema_version="1.0",
                        metadata={"entity_id": obs.subject_id},
                    )
                )
        return findings


class RepairModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = RepairCollector(ha_provider)
        self._analyzer = RepairAnalyzer()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
