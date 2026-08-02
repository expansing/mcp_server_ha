from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType


class DashboardsAnalyzer:
    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            cards = obs.data.get("cards", [])
            views = obs.data.get("views", [])
            if not views:
                findings.append(
                    Finding(
                        id=f"no-views-dashboard-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="no_views",
                        message=f"Dashboard '{obs.data.get('title', obs.subject_id)}' has no views.",
                        severity=Severity.WARNING,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"dashboard_id": obs.subject_id},
                    )
                )
            deprecated_cards = [c for c in cards if c.get("type") in ("glance", "history-graph")]
            if deprecated_cards:
                findings.append(
                    Finding(
                        id=f"deprecated-cards-dashboard-{obs.subject_id}",
                        subject_id=obs.subject_id,
                        category="deprecated_cards",
                        message=f"Dashboard '{obs.data.get('title', obs.subject_id)}' uses deprecated card types: {[c.get('type') for c in deprecated_cards]}.",
                        severity=Severity.WARNING,
                        evidence=(obs.id,),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"dashboard_id": obs.subject_id, "deprecated_types": [c.get("type") for c in deprecated_cards]},
                    )
                )
        return findings
