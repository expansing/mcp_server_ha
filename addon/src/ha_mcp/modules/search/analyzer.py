from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType


class SearchAnalyzer:
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository, query: str = ""
    ) -> list[Finding]:
        if not query:
            return []
        query_lower = query.lower()
        matched: list[Observation] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            text = " ".join(
                str(v) for v in [obs.subject_id, obs.data.get("friendly_name", ""), obs.data.get("state", "")]
            ).lower()
            if query_lower in text:
                matched.append(obs)
        if not matched:
            return []
        return [
            Finding(
                id=f"search-result-{query}",
                subject_id="search",
                category="search_result",
                message=f"Found {len(matched)} results for query '{query}'",
                severity=Severity.INFO,
                evidence=tuple(o.id for o in matched[:20]),
                confidence=1.0,
                schema_version="1.0",
                metadata={
                    "query": query,
                    "count": len(matched),
                    "entity_ids": [o.subject_id for o in matched[:20]],
                },
            )
        ]
