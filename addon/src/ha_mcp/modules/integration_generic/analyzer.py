from __future__ import annotations

from ha_mcp.graph.graph_repository import GraphRepository
from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.observation import Observation, ObservationType


class IntegrationGenericAnalyzer:
    async def analyze(self, observations: list[Observation], graph: GraphRepository) -> list[Finding]:
        findings: list[Finding] = []
        domain_stats: dict[str, dict[str, int]] = {}
        for obs in observations:
            if obs.type != ObservationType.STATE:
                continue
            domain = obs.data.get("domain", "unknown")
            state = obs.data.get("state", "")
            if domain not in domain_stats:
                domain_stats[domain] = {"total": 0, "unavailable": 0}
            domain_stats[domain]["total"] += 1
            if state == "unavailable":
                domain_stats[domain]["unavailable"] += 1
        for domain, stats in domain_stats.items():
            if stats["unavailable"] > 0:
                ratio = stats["unavailable"] / stats["total"]
                severity = Severity.CRITICAL if ratio > 0.5 else Severity.WARNING
                findings.append(
                    Finding(
                        id=f"integration-health-{domain}",
                        subject_id=domain,
                        category="integration_health",
                        message=f"Integration '{domain}': {stats['unavailable']}/{stats['total']} entities unavailable ({ratio:.0%})",
                        severity=severity,
                        evidence=(),
                        confidence=1.0,
                        schema_version="1.0",
                        metadata={"domain": domain, "unavailable": stats["unavailable"], "total": stats["total"]},
                    )
                )
        return findings
