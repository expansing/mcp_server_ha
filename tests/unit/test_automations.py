from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pytest

from ha_mcp.models.finding import Severity
from ha_mcp.models.graph_node import GraphNode
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.modules.automations.analyzer import AutomationsAnalyzer
from ha_mcp.modules.automations.module import AutomationsModule


class FakeGraphRepo:
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

    async def initialize(self, config: dict[str, Any]) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def get_automations(self) -> list[dict[str, Any]]:
        return [
            {
                "entity_id": "automation.morning",
                "alias": "Morning Routine",
                "trigger": [{"platform": "time", "at": "07:00:00"}],
                "condition": [],
                "action": [{"service": "light.turn_on", "entity_id": "light.bedroom"}],
                "enabled": True,
            },
            {
                "entity_id": "automation.disabled",
                "alias": "Disabled",
                "trigger": [],
                "condition": [],
                "action": [],
                "enabled": False,
            },
            {
                "entity_id": "automation.no_trigger",
                "alias": "No Trigger",
                "trigger": [],
                "condition": [],
                "action": [],
                "enabled": True,
            },
        ]


class TestAutomationsAnalyzer:
    @pytest.mark.asyncio
    async def test_detects_disabled_automation(self):
        analyzer = AutomationsAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="automation-automation.disabled",
                type=ObservationType.STATE,
                subject_id="automation.disabled",
                timestamp=datetime.now(tz=UTC),
                data={
                    "alias": "Disabled",
                    "trigger": [{"platform": "time", "at": "07:00:00"}],
                    "condition": [],
                    "action": [],
                    "enabled": False,
                },
                source="ha",
            )
        ]
        findings = await analyzer.analyze(obs, graph)
        assert len(findings) == 1
        assert findings[0].category == "disabled_automation"
        assert findings[0].severity == Severity.INFO

    @pytest.mark.asyncio
    async def test_detects_missing_trigger(self):
        analyzer = AutomationsAnalyzer()
        graph = FakeGraphRepo()
        obs = [
            Observation(
                id="automation-automation.no_trigger",
                type=ObservationType.STATE,
                subject_id="automation.no_trigger",
                timestamp=datetime.now(tz=UTC),
                data={
                    "alias": "No Trigger",
                    "trigger": [],
                    "condition": [],
                    "action": [],
                    "enabled": True,
                },
                source="ha",
            )
        ]
        findings = await analyzer.analyze(obs, graph)
        assert len(findings) == 1
        assert findings[0].category == "no_trigger"
        assert findings[0].severity == Severity.WARNING


class TestAutomationsModule:
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        provider = FakeHAProvider()
        module = AutomationsModule(provider)
        graph = FakeGraphRepo()
        findings = await module.run(graph)
        categories = {f.category for f in findings}
        assert "disabled_automation" in categories
        assert "no_trigger" in categories
