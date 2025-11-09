"""Pipeline orchestrating the agent workflow."""

from __future__ import annotations

from typing import Iterable, List

from .config import AgentConfig
from .models import Plan, RetrievalRequest, RetrievalResult
from .planner import Planner
from .tool_registry import ToolRegistry


class RetrievalPipeline:
    """Executes planner-generated steps using the registered tools."""

    def __init__(self, config: AgentConfig, registry: ToolRegistry) -> None:
        self._config = config
        self._planner = Planner(config=config)
        self._registry = registry

    def execute(self, request: RetrievalRequest) -> Iterable[RetrievalResult]:
        plan = self._planner.create_plan(request)
        return self._run_plan(plan, request)

    def _run_plan(self, plan: Plan, request: RetrievalRequest) -> Iterable[RetrievalResult]:
        results: List[RetrievalResult] = []
        for step in plan:
            tool = self._registry.get(step.tool_name)
            arguments = dict(step.arguments)
            if step.tool_name == "submit_result":
                arguments.setdefault("results", results)
            tool_outputs = tool.execute(request=request, **arguments)
            results.extend(tool_outputs)
        return results
