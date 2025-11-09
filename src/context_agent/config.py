"""Configuration objects and defaults for the context agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass(slots=True)
class AgentConfig:
    """Top-level configuration for the agent runtime."""

    model: str = "gpt-4o"
    workspace_root: Path = Path(".")
    temperature: float = 0.1
    max_context_tokens: int = 8192
    tool_timeout_seconds: int = 30
    enable_tracing: bool = False
    enabled_tools: List[str] = field(
        default_factory=lambda: [
            "directory_tree",
            "symbol_index",
            "file_reader",
            "ripgrep",
            "submit_result",
        ]
    )


@dataclass(slots=True)
class ToolConfig:
    """Configuration shared by all tools."""

    timeout_seconds: int = 30
