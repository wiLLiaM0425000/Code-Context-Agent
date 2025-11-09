"""Expose the context agent as an MCP tool server."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Optional

from ..app import create_app
from ..config import AgentConfig
from ..models import RetrievalIntent, RetrievalRequest, RetrievalResult


def _serialise_results(results: Iterable[RetrievalResult]) -> list[dict]:
    return [result.to_dict() for result in results]


def create_mcp_server(config: Optional[AgentConfig] = None):
    """Create an MCP server instance hosting the retrieval tool.

    Returns
    -------
    modelcontextprotocol.server.Server
        An MCP server with a single `retrieve_code_context` tool registered.
    """

    try:
        from mcp.server import Server
        from mcp.types import TextContent, ToolResult
    except ImportError as exc:  # pragma: no cover - optional dependency guard
        raise ImportError(
            "Install the `modelcontextprotocol` package to use the MCP integration."
        ) from exc

    agent_config = config or AgentConfig.from_env()
    agent = create_app(agent_config)
    server = Server("context-agent")

    @server.tool()
    def retrieve_code_context(
        workspace_path: str,
        file_path: str,
        start_line: int,
        end_line: int,
        symbol: str = "",
        intent: str = RetrievalIntent.RELATED_CONTEXT.value,
        query: str = "",
    ) -> ToolResult:
        workspace = Path(workspace_path).expanduser().resolve()
        candidate_file = Path(file_path).expanduser()
        if not candidate_file.is_absolute():
            candidate_file = (workspace / candidate_file).resolve()
        else:
            candidate_file = candidate_file.resolve()

        request = RetrievalRequest(
            workspace_path=workspace,
            file_path=candidate_file,
            start_line=int(start_line),
            end_line=int(end_line),
            symbol=symbol,
            intent=RetrievalIntent.parse(intent),
            natural_language_query=query,
        )
        results = _serialise_results(agent.run(request))
        payload = {
            "request": request.to_dict(),
            "results": results,
        }
        return ToolResult(
            content=[TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))]
        )

    return server


def run_mcp_server(config: Optional[AgentConfig] = None) -> None:
    """Run the MCP server over stdio."""

    try:
        from mcp.server import stdio
    except ImportError as exc:  # pragma: no cover - optional dependency guard
        raise ImportError(
            "Install the `modelcontextprotocol` package to launch the MCP server."
        ) from exc

    server = create_mcp_server(config=config)
    run_fn = None
    try:
        from mcp.server import run as _run

        run_fn = _run
    except ImportError:
        run_fn = None

    transport = getattr(stdio, "StdIOTransport", None)
    if transport is not None and run_fn is not None:
        run_fn(server, transport())
        return

    stdio_run = getattr(stdio, "run_server", None)
    if stdio_run is not None:
        stdio_run(server)
        return

    raise RuntimeError("Unsupported MCP stdio interface; please update the integration module.")


if __name__ == "__main__":  # pragma: no cover - module execution guard
    run_mcp_server()
