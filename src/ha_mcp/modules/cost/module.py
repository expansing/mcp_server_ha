from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class CostCollector:
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
                    id=f"cost-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data=state,
                    source="ha",
                )
            )
        return observations


class CostAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            state = obs.data.get("state", "")
            if state == "unavailable":
                findings.append(
                    Finding(
                        id=f"cost-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="cost_impact",
                        message=f"Entity {obs.subject_id} is unavailable, impacting system cost",
                        severity=__import__("ha_mcp.models.finding").Severity.WARNING,
                        evidence=(obs.id,),
                        confidence=0.7,
                        schema_version="1.0",
                        metadata={"entity_id": obs.subject_id},
                    )
                )
        return findings


class CostModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = CostCollector(ha_provider)
        self._analyzer = CostAnalyzer()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
