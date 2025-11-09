"""Domain models shared across the agent pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional


class RetrievalIntent(str, Enum):
    """Supported retrieval intents."""

    SYMBOL_IMPLEMENTATION = "symbol_implementation"
    SYMBOL_REFERENCES = "symbol_references"
    SYMBOL_DEFINITION = "symbol_definition"
    VALUE_LOOKUP = "value_lookup"
    RELATED_CONTEXT = "related_context"


@dataclass(slots=True)
class RetrievalRequest:
    """User provided retrieval request."""

    workspace_path: Path
    file_path: Path
    start_line: int
    end_line: int
    symbol: str
    intent: RetrievalIntent
    natural_language_query: str


@dataclass(slots=True)
class RetrievalResult:
    """Result returned by the retrieval pipeline."""

    file_path: Path
    start_line: int
    end_line: int
    code_snippet: str
    confidence: float
    notes: Optional[str] = None


@dataclass(slots=True)
class PlanStep:
    """Single action the planner determines should be executed."""

    description: str
    tool_name: str
    arguments: dict


@dataclass(slots=True)
class Plan:
    """A collection of :class:`PlanStep` objects."""

    steps: List[PlanStep]

    def __iter__(self) -> Iterable[PlanStep]:
        return iter(self.steps)
