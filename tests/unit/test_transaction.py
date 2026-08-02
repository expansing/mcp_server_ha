from __future__ import annotations

import os
import tempfile
from datetime import datetime

import pytest

from ha_mcp.models.staged_edit import EditType, StagedEdit
from ha_mcp.transaction.transaction_manager import (
    Transaction,
    TransactionManager,
    TransactionStatus,
    ValidationResult,
)


class TestTransactionStatus:
    def test_values(self):
        assert TransactionStatus.OPEN.value == "open"
        assert TransactionStatus.VALIDATING.value == "validating"
        assert TransactionStatus.COMMITTING.value == "committing"
        assert TransactionStatus.COMMITTED.value == "committed"
        assert TransactionStatus.ROLLED_BACK.value == "rolled_back"
        assert TransactionStatus.FAILED.value == "failed"


class TestTransaction:
    def test_fields(self):
        tx = Transaction(
            id="tx1",
            description="test",
            status=TransactionStatus.OPEN,
            created_at=datetime.now(),
            requested_by="user",
            tool_name="tool",
        )
        assert tx.id == "tx1"
        assert tx.requested_by == "user"
        assert tx.tool_name == "tool"
        assert tx.status == TransactionStatus.OPEN
        assert tx.edits == []
        assert tx.committed_at is None


class TestTransactionManager:
    @pytest.mark.asyncio
    async def test_create_transaction(self):
        manager = TransactionManager()
        tx = await manager.create("desc", "user", "tool")
        assert tx.requested_by == "user"
        assert tx.tool_name == "tool"
        assert tx.status == TransactionStatus.OPEN

    @pytest.mark.asyncio
    async def test_add_edit(self):
        manager = TransactionManager()
        tx = await manager.create("desc", "user", "tool")
        edit = StagedEdit(
            id="e1",
            type=EditType.FILE_WRITE,
            target="f",
            content="",
            diff="",
        )
        await manager.add_edit(tx.id, edit)
        retrieved = manager.get(tx.id)
        assert len(retrieved.edits) == 1

    @pytest.mark.asyncio
    async def test_validate_empty_transaction(self):
        manager = TransactionManager()
        tx = await manager.create("desc", "user", "tool")
        results = await manager.validate(tx.id)
        assert len(results) == 1
        assert not results[0].passed
        assert "No edits" in results[0].message

    @pytest.mark.asyncio
    async def test_commit_writes_file(self, tmp_path):
        manager = TransactionManager()
        tx = await manager.create("desc", "user", "tool")
        target = str(tmp_path / "output.txt")
        edit = StagedEdit(
            id="e1",
            type=EditType.FILE_WRITE,
            target=target,
            content="hello world",
            diff="",
        )
        await manager.add_edit(tx.id, edit)
        committed = await manager.commit(tx.id)
        assert committed.status == TransactionStatus.COMMITTED
        assert committed.committed_at is not None
        with open(target, "r", encoding="utf-8") as f:
            assert f.read() == "hello world"

    @pytest.mark.asyncio
    async def test_commit_fails_on_bad_edit(self):
        manager = TransactionManager()
        tx = await manager.create("desc", "user", "tool")
        edit = StagedEdit(
            id="e1",
            type=EditType.FILE_WRITE,
            target="/nonexistent/path/file.txt",
            content="hello",
            diff="",
        )
        await manager.add_edit(tx.id, edit)
        committed = await manager.commit(tx.id)
        assert committed.status == TransactionStatus.FAILED

    @pytest.mark.asyncio
    async def test_verify_success(self, tmp_path):
        manager = TransactionManager()
        tx = await manager.create("desc", "user", "tool")
        target = str(tmp_path / "output.txt")
        edit = StagedEdit(
            id="e1",
            type=EditType.FILE_WRITE,
            target=target,
            content="hello",
            diff="",
        )
        await manager.add_edit(tx.id, edit)
        await manager.commit(tx.id)
        result = await manager.verify(tx.id)
        assert result.passed
        assert "verified" in result.message.lower()

    @pytest.mark.asyncio
    async def test_verify_not_committed(self):
        manager = TransactionManager()
        tx = await manager.create("desc", "user", "tool")
        result = await manager.verify(tx.id)
        assert not result.passed
        assert "not found" in result.message.lower() or "committed" in result.message.lower()
