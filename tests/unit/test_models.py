from __future__ import annotations

from datetime import datetime

import pytest
from dataclasses import FrozenInstanceError

from ha_mcp.models.finding import Finding, Severity
from ha_mcp.models.graph_node import GraphNode, ResourceKind
from ha_mcp.models.observation import Observation, ObservationType
from ha_mcp.models.recommendation import Effort, Recommendation, Risk
from ha_mcp.models.staged_edit import EditType, StagedEdit


class TestFrozenModels:
    def test_graph_node_immutable(self):
        node = GraphNode(
            id="node1",
            resource_kind=ResourceKind.ENTITY,
        )
        with pytest.raises(FrozenInstanceError):
            node.id = "new_id"

    def test_observation_immutable(self):
        obs = Observation(
            id="obs1",
            type=ObservationType.STATE,
            subject_id="node1",
            timestamp=datetime.now(),
            data={},
            source="ha",
        )
        with pytest.raises(FrozenInstanceError):
            obs.id = "new_id"

    def test_finding_immutable(self):
        finding = Finding(
            id="find1",
            subject_id="node1",
            category="rule1",
            message="msg",
            severity=Severity.INFO,
        )
        with pytest.raises(FrozenInstanceError):
            finding.id = "new_id"

    def test_recommendation_immutable(self):
        rec = Recommendation(
            id="rec1",
            finding_ids=(),
            action="fix",
            rationale="because",
            effort=Effort.EASY,
            risk=Risk.LOW,
            priority="high",
            automatable=True,
        )
        with pytest.raises(FrozenInstanceError):
            rec.id = "new_id"

    def test_staged_edit_immutable(self):
        edit = StagedEdit(
            id="edit1",
            type=EditType.FILE_WRITE,
            target="file.yaml",
            content="",
            diff="",
        )
        with pytest.raises(FrozenInstanceError):
            edit.id = "new_id"
