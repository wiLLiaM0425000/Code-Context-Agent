"""Registry mapping tool names to executable implementations."""

from __future__ import annotations

from typing import Dict

from .config import AgentConfig
from .tools.base import BaseTool
from .tools.directory_tree import DirectoryTreeTool
from .tools.file_reader import FileReaderTool
from .tools.report import SubmitResultTool
from .tools.ripgrep import RipGrepTool
from .tools.symbol_index import SymbolIndexTool


class ToolRegistry:
    """Maintains a mapping of logical tool names to tool instances."""

    def __init__(self, tools: Dict[str, BaseTool]) -> None:
        self._tools = tools

    def get(self, tool_name: str) -> BaseTool:
        try:
            return self._tools[tool_name]
        except KeyError as exc:  # pragma: no cover - simple guard
            raise ValueError(f"Tool '{tool_name}' is not registered") from exc

    @classmethod
    def from_config(cls, config: AgentConfig) -> "ToolRegistry":
        tools: Dict[str, BaseTool] = {
            "directory_tree": DirectoryTreeTool(config=config),
            "symbol_index": SymbolIndexTool(config=config),
            "file_reader": FileReaderTool(config=config),
            "ripgrep": RipGrepTool(config=config),
            "submit_result": SubmitResultTool(config=config),
        }

        active_tools = {
            name: tool for name, tool in tools.items() if name in config.enabled_tools
        }
        return cls(tools=active_tools)
