"""Base classes and shared utilities for tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol

from ..config import AgentConfig, ToolConfig
from ..models import RetrievalRequest, RetrievalResult


class ToolExecutionError(RuntimeError):
    """Raised when a tool fails to execute."""


class SupportsExecute(Protocol):
    """Protocol describing the execute contract for tools."""

    def execute(self, request: RetrievalRequest, **kwargs) -> Iterable[RetrievalResult]:
        ...


@dataclass
class BaseTool:
    """Base class for concrete tool implementations."""

    config: AgentConfig
    tool_config: ToolConfig = field(default_factory=ToolConfig)

    def execute(self, request: RetrievalRequest, **kwargs) -> Iterable[RetrievalResult]:
        raise NotImplementedError
