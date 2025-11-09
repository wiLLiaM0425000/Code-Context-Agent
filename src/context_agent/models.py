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

    @classmethod
    def parse(cls, value: str) -> "RetrievalIntent":
        """Parse a string value into a :class:`RetrievalIntent`."""

        try:
            return cls(value)
        except ValueError as exc:  # pragma: no cover - validation guard
            valid = ", ".join(intent.value for intent in cls)
            raise ValueError(f"Unsupported retrieval intent '{value}'. Options: {valid}") from exc


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

    def to_dict(self) -> dict:
        """Return a serialisable representation of the request."""

        return {
            "workspace_path": str(self.workspace_path),
            "file_path": str(self.file_path),
            "start_line": self.start_line,
            "end_line": self.end_line,
            "symbol": self.symbol,
            "intent": self.intent.value,
            "natural_language_query": self.natural_language_query,
        }


@dataclass(slots=True)
class RetrievalResult:
    """Result returned by the retrieval pipeline."""

    file_path: Path
    start_line: int
    end_line: int
    code_snippet: str
    confidence: float
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the result into a JSON serialisable dictionary."""

        return {
            "file_path": str(self.file_path),
            "start_line": self.start_line,
            "end_line": self.end_line,
            "code_snippet": self.code_snippet,
            "confidence": self.confidence,
            "notes": self.notes,
        }


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
