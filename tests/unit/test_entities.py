from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from ha_mcp.analysis.pipeline import Collector
from ha_mcp.models.finding import Severity
from ha_mcp.models.graph_node import GraphNode
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.staged_edit import EditType
from ha_mcp.modules.entities.action import NotifyAction
from ha_mcp.modules.entities.analyzer import EntitiesAnalyzer
from ha_mcp.modules.entities.collector import EntitiesCollector


class MinimalGraphRepo:
    def __init__(self) -> None:
        self._nodes: dict[str, GraphNode] = {}

    async def get_node(self, node_id: str) -> GraphNode | None:
        return self._nodes.get(node_id)

    async def neighbors(self, node_id: str, direction: str = "both") -> list[GraphNode]:
        return []

    async def find(self, query: dict[str, Any]) -> list[GraphNode]:
        return list(self._nodes.values())

    async def search(self, text: str) -> list[GraphNode]:
        return []

    async def update(self, node: GraphNode) -> None:
        self._nodes[node.id] = node

    async def remove(self, node_id: str) -> None:
        self._nodes.pop(node_id, None)


class FakeHAProvider:
    name = "ha"
    capabilities = frozenset()

    async def get_states(self) -> list[dict[str, Any]]:
        return [
            {
                "entity_id": "sensor.temp",
                "state": "20",
                "attributes": {"unit_of_measurement": "°C"},
                "last_changed": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
            },
            {
                "entity_id": "sensor.stale",
                "state": "unavailable",
                "attributes": {},
                "last_changed": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
            },
        ]


class TestEntitiesCollector:
    def test_conforms_to_protocol(self):
        provider = FakeHAProvider()
        collector = EntitiesCollector(provider)
        assert isinstance(collector, Collector)

    @pytest.mark.asyncio
    async def test_collect_returns_observations(self):
        provider = FakeHAProvider()
        collector = EntitiesCollector(provider)
        graph = MinimalGraphRepo()
        observations = await collector.collect(graph)
        assert len(observations) == 2
        entity_ids = {o.subject_id for o in observations}
        assert "sensor.temp" in entity_ids
        assert "sensor.stale" in entity_ids


class TestEntitiesAnalyzer:
    @pytest.mark.asyncio
    async def test_detects_stale_entity(self):
        analyzer = EntitiesAnalyzer(stale_threshold_days=7)
        graph = MinimalGraphRepo()
        stale_obs = Observation(
            id="state-sensor.stale",
            type=ObservationType.STATE,
            subject_id="sensor.stale",
            timestamp=datetime.now(tz=UTC),
            data={
                "state": "unavailable",
                "attributes": {},
                "last_changed": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(days=10)).isoformat(),
            },
            source="ha",
        )
        findings = await analyzer.analyze([stale_obs], graph)
        categories = {f.category for f in findings}
        assert "stale_entity" in categories
        assert any(f.severity == Severity.WARNING for f in findings)
        assert any(f.schema_version == "1.0" for f in findings)

    @pytest.mark.asyncio
    async def test_ignores_recently_unavailable(self):
        analyzer = EntitiesAnalyzer(stale_threshold_days=7)
        graph = MinimalGraphRepo()
        recent_obs = Observation(
            id="state-sensor.recent",
            type=ObservationType.STATE,
            subject_id="sensor.recent",
            timestamp=datetime.now(tz=UTC),
            data={
                "state": "unavailable",
                "attributes": {},
                "last_changed": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
            },
            source="ha",
        )
        findings = await analyzer.analyze([recent_obs], graph)
        categories = {f.category for f in findings}
        assert "stale_entity" not in categories

    @pytest.mark.asyncio
    async def test_ignores_available_entities(self):
        analyzer = EntitiesAnalyzer(stale_threshold_days=7)
        graph = MinimalGraphRepo()
        available_obs = Observation(
            id="state-sensor.ok",
            type=ObservationType.STATE,
            subject_id="sensor.ok",
            timestamp=datetime.now(tz=UTC),
            data={
                "state": "20",
                "attributes": {},
                "last_changed": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
            },
            source="ha",
        )
        findings = await analyzer.analyze([available_obs], graph)
        categories = {f.category for f in findings}
        assert "stale_entity" not in categories
        assert "unknown_entity" not in categories

    @pytest.mark.asyncio
    async def test_detects_unknown_state(self):
        analyzer = EntitiesAnalyzer(stale_threshold_days=7)
        graph = MinimalGraphRepo()
        unknown_obs = Observation(
            id="state-sensor.unknown",
            type=ObservationType.STATE,
            subject_id="sensor.unknown",
            timestamp=datetime.now(tz=UTC),
            data={
                "state": "unknown",
                "attributes": {"unit_of_measurement": "°C"},
                "last_changed": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
            },
            source="ha",
        )
        findings = await analyzer.analyze([unknown_obs], graph)
        assert len(findings) == 1
        assert findings[0].category == "unknown_entity"
        assert findings[0].severity == Severity.WARNING

    @pytest.mark.asyncio
    async def test_detects_missing_attributes(self):
        analyzer = EntitiesAnalyzer(stale_threshold_days=7)
        graph = MinimalGraphRepo()
        no_attrs_obs = Observation(
            id="state-sensor.noattrs",
            type=ObservationType.STATE,
            subject_id="sensor.noattrs",
            timestamp=datetime.now(tz=UTC),
            data={
                "state": "20",
                "attributes": {},
                "last_changed": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
                "last_updated": (datetime.now(tz=UTC) - timedelta(hours=1)).isoformat(),
            },
            source="ha",
        )
        findings = await analyzer.analyze([no_attrs_obs], graph)
        assert len(findings) == 1
        assert findings[0].category == "missing_attributes"
        assert findings[0].severity == Severity.INFO


class TestNotifyAction:
    @pytest.mark.asyncio
    async def test_compile_creates_staged_edit(self):
        action = NotifyAction()
        recommendation = type("R", (), {
            "finding_id": "f1",
            "title": "Test",
            "description": "desc",
        })()
        edits = await action.compile(recommendation, {})
        assert len(edits) == 1
        assert edits[0].type == EditType.SERVICE_CALL


class TestEntitiesModule:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        provider = FakeHAProvider()
        from ha_mcp.modules.entities.module import EntitiesModule
        module = EntitiesModule(provider)
        graph = MinimalGraphRepo()
        findings = await module.run(graph)
        categories = {f.category for f in findings}
        assert "stale_entity" in categories
