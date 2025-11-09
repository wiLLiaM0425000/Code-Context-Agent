"""LLM-powered planner that determines which tools to run."""

from __future__ import annotations

from dataclasses import dataclass

from .config import AgentConfig
from .models import Plan, PlanStep, RetrievalIntent, RetrievalRequest


@dataclass
class Planner:
    """Orchestrates plan generation by delegating to the LLM."""

    config: AgentConfig

    def create_plan(self, request: RetrievalRequest) -> Plan:
        """Create a plan stub based on the request intent.

        In a full implementation this method would call the LLM to propose
        tool invocations. For now we generate a deterministic scaffold to
        illustrate the orchestration flow.
        """

        if request.intent == RetrievalIntent.SYMBOL_IMPLEMENTATION:
            steps = [
                PlanStep(
                    description="Find implementations of the target symbol",
                    tool_name="symbol_index",
                    arguments={"symbol": request.symbol},
                )
            ]
        elif request.intent == RetrievalIntent.SYMBOL_REFERENCES:
            steps = [
                PlanStep(
                    description="Search for references to the symbol",
                    tool_name="ripgrep",
                    arguments={"pattern": request.symbol},
                )
            ]
        else:
            steps = [
                PlanStep(
                    description="Read the relevant file segment",
                    tool_name="file_reader",
                    arguments={
                        "file_path": request.file_path,
                        "start_line": request.start_line,
                        "end_line": request.end_line,
                    },
                )
            ]

        steps.append(
            PlanStep(
                description="Submit collated retrieval results",
                tool_name="submit_result",
                arguments={},
            )
        )

        return Plan(steps=steps)
