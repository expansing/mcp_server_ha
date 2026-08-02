from __future__ import annotations

import importlib
import pkgutil
from typing import Any

from ha_mcp.graph.graph_repository_impl import GraphRepositoryImpl
from ha_mcp.models.finding import Finding
from ha_mcp.models.recommendation import Recommendation
from ha_mcp.models.tool_result import ToolResult
from ha_mcp.transaction.transaction_manager import TransactionManager


class App:
    def __init__(self) -> None:
        self._registry: Any = None
        self._tx_manager = TransactionManager()
        self._modules: dict[str, Any] = {}
        self._graph = GraphRepositoryImpl()
        self._provider: Any = None

    def set_registry(self, registry: Any) -> None:
        self._registry = registry

    def set_provider(self, provider: Any) -> None:
        self._provider = provider

    def register_module(self, name: str, module: Any) -> None:
        self._modules[name] = module

    def auto_register_modules(self, package_name: str = "ha_mcp.modules") -> None:
        package = importlib.import_module(package_name)
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            if not is_pkg:
                continue
            full_name = f"{package_name}.{module_name}"
            try:
                mod = importlib.import_module(f"{full_name}.module")
                module_cls = None
                for attr_name in dir(mod):
                    if attr_name.endswith("Module") and attr_name != "Module":
                        module_cls = getattr(mod, attr_name)
                        break
                if module_cls and self._provider:
                    self._modules[module_name] = module_cls(self._provider)
            except Exception:
                continue

    async def initialize(self, config: dict[str, Any]) -> None:
        if self._registry:
            await self._registry.initialize_all(config)
        elif self._provider:
            await self._provider.initialize(config.get(self._provider.name, {}))

    async def shutdown(self) -> None:
        if self._registry:
            await self._registry.shutdown_all()
        elif self._provider:
            await self._provider.shutdown()

    async def _compile_recommendations(
        self, findings: list[Finding], module: Any
    ) -> tuple[list[Recommendation], list[Any]]:
        recommendations: list[Recommendation] = []
        all_edits: list[Any] = []
        for finding in findings:
            recommendation = Recommendation(
                id=f"rec-{finding.id}",
                finding_ids=(finding.id,),
                action="notify",
                rationale=finding.message,
                effort="trivial",
                risk="none",
                priority="medium",
                automatable=True,
            )
            recommendations.append(recommendation)
            if hasattr(module, "_action"):
                try:
                    edits = await module._action.compile(
                        recommendation, {"entity_id": finding.subject_id}
                    )
                    all_edits.extend(edits)
                except Exception:
                    continue
        return recommendations, all_edits

    async def run_module(self, module_name: str, requested_by: str = "system") -> ToolResult:
        module = self._modules.get(module_name)
        if not module:
            return ToolResult(
                status="error",
                summary=f"Module '{module_name}' not found",
                findings=[],
                recommendations=[],
                details={"error": f"Module '{module_name}' not found"},
            )

        tx = await self._tx_manager.create(
            description=f"Run module: {module_name}",
            requested_by=requested_by,
            tool_name="app.run_module",
        )

        try:
            findings = await module.run(self._graph)
            recommendations, edits = await self._compile_recommendations(findings, module)
            for edit in edits:
                await self._tx_manager.add_edit(tx.id, edit)
            return ToolResult(
                status="success",
                summary=f"Module '{module_name}' completed",
                findings=findings,
                recommendations=recommendations,
                details={"transaction_id": tx.id},
                transaction_id=tx.id,
            )
        except Exception as exc:
            await self._tx_manager.rollback(tx.id)
            return ToolResult(
                status="error",
                summary=f"Module '{module_name}' failed",
                findings=[],
                recommendations=[],
                details={"error": str(exc), "transaction_id": tx.id},
                transaction_id=tx.id,
            )
