"""High-level factory for the code context retrieval agent."""

from __future__ import annotations

from typing import Iterable, Optional

from .config import AgentConfig
from .models import RetrievalRequest, RetrievalResult
from .pipeline import RetrievalPipeline
from .tool_registry import ToolRegistry


class ContextAgent:
    """Facade that coordinates planning and tool execution for retrieval tasks."""

    def __init__(self, config: AgentConfig, pipeline: RetrievalPipeline) -> None:
        self._config = config
        self._pipeline = pipeline

    @property
    def config(self) -> AgentConfig:
        """Return the agent configuration."""

        return self._config

    def run(self, request: RetrievalRequest) -> Iterable[RetrievalResult]:
        """Execute the retrieval pipeline for the provided request."""

        return self._pipeline.execute(request)


def create_app(config: Optional[AgentConfig] = None) -> ContextAgent:
    """Create a fully configured :class:`ContextAgent`."""

    agent_config = config or AgentConfig.from_env()
    registry = ToolRegistry.from_config(agent_config)
    pipeline = RetrievalPipeline(config=agent_config, registry=registry)
    return ContextAgent(config=agent_config, pipeline=pipeline)
