from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from ha_mcp.analysis.pipeline import Analyzer
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.graph.graph_repository import GraphRepository


class EntitiesAnalyzer:
    def __init__(self, stale_threshold_days: int = 7) -> None:
        self._stale_threshold = timedelta(days=stale_threshold_days)

    async def analyze(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        findings.extend(await self._detect_stale_entities(observations, graph))
        findings.extend(await self._detect_unknown_states(observations, graph))
        findings.extend(await self._detect_missing_attributes(observations, graph))
        return findings

    async def _detect_stale_entities(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        now = datetime.now()
        entity_observations = [
            o for o in observations if o.type == ObservationType.STATE
        ]
        for obs in entity_observations:
            state = obs.data.get("state")
            if state != "unavailable":
                continue
            last_changed_str = obs.data.get("last_changed") or obs.timestamp.isoformat()
            try:
                last_changed = datetime.fromisoformat(last_changed_str)
            except (ValueError, TypeError):
                continue
            if now - last_changed < self._stale_threshold:
                continue
            node = await graph.get_node(obs.subject_id)
            attributes = node.attributes if node else {}
            entity_name = attributes.get("name", obs.subject_id)
            integration_domain = node.integration_domain if node else None
            integration = integration_domain or "unknown"
            findings.append(
                Finding(
                    id=f"stale-entity-{obs.subject_id}",
                    subject_id=obs.subject_id,
                    category="stale_entity",
                    message=(
                        f"Entity {obs.subject_id} (integration: {integration}) "
                        f"has been in 'unavailable' state since {last_changed_str}. "
                        f"This may indicate a failed integration, disconnected device, or misconfiguration."
                    ),
                    severity=Severity.WARNING,
                    evidence=(obs.id,),
                    confidence=1.0,
                    schema_version="1.0",
                    metadata={
                        "entity_id": obs.subject_id,
                        "integration_domain": integration,
                        "unavailable_since": last_changed_str,
                        "stale_days": (now - last_changed).days,
                    },
                )
            )
        return findings

    async def _detect_unknown_states(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            state = obs.data.get("state")
            if state != "unknown":
                continue
            node = await graph.get_node(obs.subject_id)
            attributes = node.attributes if node else {}
            entity_name = attributes.get("name", obs.subject_id)
            findings.append(
                Finding(
                    id=f"unknown-entity-{obs.subject_id}",
                    subject_id=obs.subject_id,
                    category="unknown_entity",
                    message=(
                        f"Entity {obs.subject_id} ({entity_name}) is in 'unknown' state. "
                        f"This typically means the integration cannot determine the current state."
                    ),
                    severity=Severity.WARNING,
                    evidence=(obs.id,),
                    confidence=0.9,
                    schema_version="1.0",
                    metadata={
                        "entity_id": obs.subject_id,
                        "entity_name": entity_name,
                    },
                )
            )
        return findings

    async def _detect_missing_attributes(
        self, observations: list[Observation], graph: GraphRepository
    ) -> list[Finding]:
        findings: list[Finding] = []
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            attrs = obs.data.get("attributes", {})
            if attrs:
                continue
            node = await graph.get_node(obs.subject_id)
            attributes = node.attributes if node else {}
            entity_name = attributes.get("name", obs.subject_id)
            findings.append(
                Finding(
                    id=f"missing-attrs-{obs.subject_id}",
                    subject_id=obs.subject_id,
                    category="missing_attributes",
                    message=(
                        f"Entity {obs.subject_id} ({entity_name}) has no attributes. "
                        f"This may indicate a misconfigured entity or integration issue."
                    ),
                    severity=Severity.INFO,
                    evidence=(obs.id,),
                    confidence=0.7,
                    schema_version="1.0",
                    metadata={
                        "entity_id": obs.subject_id,
                        "entity_name": entity_name,
                    },
                )
            )
        return findings
