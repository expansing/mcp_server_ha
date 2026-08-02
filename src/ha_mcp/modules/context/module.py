from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.provider_protocol import Provider


class ContextCollector:
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
                    id=f"context-{entity_id}",
                    type=ObservationType.STATE,
                    subject_id=entity_id,
                    timestamp=__import__("datetime").datetime.now(),
                    data=state,
                    source="ha",
                )
            )
        return observations


class ContextAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        return []


class ContextModule:
    def __init__(self, ha_provider: Provider) -> None:
        self._collector = ContextCollector(ha_provider)
        self._analyzer = ContextAnalyzer()

    async def run(self, graph: GraphRepository) -> list[Finding]:
        observations = await self._collector.collect(graph)
        findings = await self._analyzer.analyze(observations, graph)
        return findings
