"""Configuration objects and defaults for the context agent."""

from __future__ import annotations

import contextlib
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(slots=True)
class AgentConfig:
    """Top-level configuration for the agent runtime."""

    model: str = "gpt-4o"
    workspace_root: Path = Path(".")
    temperature: float = 0.1
    max_context_tokens: int = 8192
    tool_timeout_seconds: int = 30
    enable_tracing: bool = False
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    openai_organization: Optional[str] = None
    enabled_tools: List[str] = field(
        default_factory=lambda: [
            "directory_tree",
            "symbol_index",
            "file_reader",
            "ripgrep",
            "submit_result",
        ]
    )

    @classmethod
    def from_env(cls, **overrides: Any) -> "AgentConfig":
        """Create a configuration instance using environment defaults."""

        data: Dict[str, Any] = {}

        env_workspace = overrides.pop("workspace_root", None)
        if env_workspace is None:
            env_workspace = os.getenv("CONTEXT_AGENT_WORKSPACE")
        if env_workspace is not None:
            data["workspace_root"] = Path(env_workspace)

        env_model = overrides.pop("model", None)
        if env_model is None:
            env_model = os.getenv("OPENAI_MODEL") or os.getenv("CONTEXT_AGENT_MODEL")
        if env_model:
            data["model"] = env_model

        env_temperature = overrides.pop("temperature", None)
        if env_temperature is None and (temp := os.getenv("CONTEXT_AGENT_TEMPERATURE")):
            with contextlib.suppress(ValueError):
                env_temperature = float(temp)
        if env_temperature is not None:
            data["temperature"] = env_temperature

        env_timeout = overrides.pop("tool_timeout_seconds", None)
        if env_timeout is None and (timeout := os.getenv("CONTEXT_AGENT_TOOL_TIMEOUT")):
            with contextlib.suppress(ValueError):
                env_timeout = int(timeout)
        if env_timeout is not None:
            data["tool_timeout_seconds"] = env_timeout

        api_key = overrides.pop("openai_api_key", None)
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            data["openai_api_key"] = api_key

        base_url = overrides.pop("openai_base_url", None)
        if base_url is None:
            base_url = os.getenv("OPENAI_BASE_URL")
        if base_url:
            data["openai_base_url"] = base_url

        organization = overrides.pop("openai_organization", None)
        if organization is None:
            organization = os.getenv("OPENAI_ORGANIZATION")
        if organization:
            data["openai_organization"] = organization

        enabled_tools = overrides.pop("enabled_tools", None)
        if enabled_tools is None and (tools := os.getenv("CONTEXT_AGENT_ENABLED_TOOLS")):
            enabled_tools = [tool.strip() for tool in tools.split(",") if tool.strip()]
        if enabled_tools is not None:
            data["enabled_tools"] = enabled_tools

        for field_name, value in overrides.items():
            if value is not None:
                if field_name == "workspace_root" and not isinstance(value, Path):
                    data[field_name] = Path(value)
                else:
                    data[field_name] = value

        return cls(**data)


@dataclass(slots=True)
class ToolConfig:
    """Configuration shared by all tools."""

    timeout_seconds: int = 30
