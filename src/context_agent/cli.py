"""Command line interface for running the context agent locally."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .app import create_app
from .config import AgentConfig
from .models import RetrievalIntent, RetrievalRequest

app = typer.Typer(help="Run the code context retrieval agent from the command line.")


def _parse_intent(value: str) -> RetrievalIntent:
    try:
        return RetrievalIntent.parse(value)
    except ValueError as exc:  # pragma: no cover - user input guard
        raise typer.BadParameter(str(exc)) from exc


@app.command()
def run(
    workspace: Path = typer.Argument(..., help="Path to the local repository to inspect."),
    file_path: Path = typer.Argument(..., help="File path containing the seed snippet."),
    start_line: int = typer.Argument(..., help="Start line of the snippet."),
    end_line: int = typer.Argument(..., help="End line of the snippet."),
    symbol: str = typer.Option("", "--symbol", help="Symbol to focus on during retrieval."),
    intent: str = typer.Option(
        RetrievalIntent.RELATED_CONTEXT.value,
        "--intent",
        help="Retrieval intent guiding the workflow.",
        callback=_parse_intent,
    ),
    query: Optional[str] = typer.Option(
        None, "--query", help="Natural language description of the retrieval goal."
    ),
    openai_api_key: Optional[str] = typer.Option(
        None,
        "--openai-api-key",
        envvar="OPENAI_API_KEY",
        help="API key used for planner calls. Defaults to OPENAI_API_KEY env var if set.",
    ),
    openai_base_url: Optional[str] = typer.Option(
        None,
        "--openai-base-url",
        envvar="OPENAI_BASE_URL",
        help="Optional custom base URL for OpenAI-compatible endpoints.",
    ),
    openai_model: Optional[str] = typer.Option(
        None,
        "--openai-model",
        envvar="OPENAI_MODEL",
        help="Override the model used when querying OpenAI.",
    ),
    openai_org: Optional[str] = typer.Option(
        None,
        "--openai-organization",
        envvar="OPENAI_ORGANIZATION",
        help="OpenAI organisation identifier, if required.",
    ),
) -> None:
    """Execute the retrieval workflow and print the aggregated results as JSON."""

    workspace = workspace.expanduser().resolve()
    resolved_file = file_path.expanduser()
    if not resolved_file.is_absolute():
        resolved_file = (workspace / resolved_file).resolve()
    else:
        resolved_file = resolved_file.resolve()

    intent_enum = intent if isinstance(intent, RetrievalIntent) else RetrievalIntent.parse(intent)

    config = AgentConfig.from_env(
        workspace_root=workspace,
        openai_api_key=openai_api_key,
        openai_base_url=openai_base_url,
        openai_organization=openai_org,
        model=openai_model,
    )

    agent = create_app(config=config)
    request = RetrievalRequest(
        workspace_path=workspace,
        file_path=resolved_file,
        start_line=start_line,
        end_line=end_line,
        symbol=symbol,
        intent=intent_enum,
        natural_language_query=query or "",
    )

    results = [result.to_dict() for result in agent.run(request)]
    payload = {
        "request": request.to_dict(),
        "results": results,
        "config": {
            "model": config.model,
            "workspace_root": str(config.workspace_root),
            "openai_base_url": config.openai_base_url,
            "openai_organization": config.openai_organization,
            "openai_configured": bool(config.openai_api_key),
        },
    }

    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> None:  # pragma: no cover - CLI entry point
    app()


if __name__ == "__main__":  # pragma: no cover - CLI execution guard
    main()
