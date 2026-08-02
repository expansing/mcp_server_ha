from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ha_mcp.models.staged_edit import EditType, StagedEdit


class TransactionStatus(str, Enum):
    OPEN = "open"
    VALIDATING = "validating"
    COMMITTING = "committing"
    COMMITTED = "committed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class ValidationResult:
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Transaction:
    id: str
    description: str
    status: TransactionStatus
    created_at: datetime
    edits: list[StagedEdit] = field(default_factory=list)
    validation_results: list[ValidationResult] = field(default_factory=list)
    requested_by: str = ""
    tool_name: str = ""
    committed_at: datetime | None = None


class TransactionManager:
    def __init__(self) -> None:
        self._transactions: dict[str, Transaction] = {}

    async def create(
        self, description: str, requested_by: str, tool_name: str
    ) -> Transaction:
        tx = Transaction(
            id=uuid.uuid4().hex,
            description=description,
            status=TransactionStatus.OPEN,
            created_at=datetime.now(),
            requested_by=requested_by,
            tool_name=tool_name,
        )
        self._transactions[tx.id] = tx
        return tx

    async def add_edit(self, transaction_id: str, edit: StagedEdit) -> None:
        tx = self._transactions.get(transaction_id)
        if tx is not None:
            tx.edits.append(edit)

    async def validate(self, transaction_id: str) -> list[ValidationResult]:
        tx = self._transactions.get(transaction_id)
        if tx is None:
            return [ValidationResult(passed=False, message="Transaction not found")]
        results: list[ValidationResult] = []
        if not tx.edits:
            results.append(ValidationResult(passed=False, message="No edits to validate"))
        for edit in tx.edits:
            if not edit.id:
                results.append(ValidationResult(passed=False, message=f"Edit missing id: {edit}"))
            if not edit.target:
                results.append(ValidationResult(passed=False, message=f"Edit missing target: {edit}"))
        tx.validation_results = results
        return results

    async def commit(self, transaction_id: str) -> Transaction:
        tx = self._transactions.get(transaction_id)
        if tx is None:
            return tx
        tx.status = TransactionStatus.COMMITTING
        validation = await self.validate(transaction_id)
        if any(not v.passed for v in validation):
            tx.status = TransactionStatus.FAILED
            return tx
        for edit in tx.edits:
            if edit.type == EditType.FILE_WRITE:
                try:
                    with open(edit.target, "w", encoding="utf-8") as f:
                        f.write(edit.content if isinstance(edit.content, str) else str(edit.content))
                except Exception:
                    tx.status = TransactionStatus.FAILED
                    return tx
        tx.status = TransactionStatus.COMMITTED
        tx.committed_at = datetime.now()
        return tx

    async def verify(self, transaction_id: str) -> ValidationResult:
        tx = self._transactions.get(transaction_id)
        if tx is None:
            return ValidationResult(passed=False, message="Transaction not found")
        if tx.status != TransactionStatus.COMMITTED:
            return ValidationResult(passed=False, message=f"Transaction is {tx.status}, not committed")
        return ValidationResult(passed=True, message="Transaction verified successfully")

    async def rollback(self, transaction_id: str) -> Transaction:
        tx = self._transactions.get(transaction_id)
        if tx is not None:
            tx.status = TransactionStatus.ROLLED_BACK
        return tx

    def get(self, transaction_id: str) -> Transaction | None:
        return self._transactions.get(transaction_id)
