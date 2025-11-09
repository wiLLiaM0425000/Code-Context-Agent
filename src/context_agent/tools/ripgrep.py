"""Tool for performing project-wide textual search using ripgrep."""

from __future__ import annotations

import subprocess
from typing import Iterable

from ..models import RetrievalRequest, RetrievalResult
from .base import BaseTool, ToolExecutionError


class RipGrepTool(BaseTool):
    """Invoke ripgrep to find keyword matches in the workspace."""

    def execute(self, request: RetrievalRequest, **kwargs) -> Iterable[RetrievalResult]:
        pattern = kwargs["pattern"]
        root = request.workspace_path
        command = [
            "rg",
            "--line-number",
            "--color=never",
            pattern,
            str(root),
        ]

        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.tool_config.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:  # pragma: no cover - guard
            raise ToolExecutionError("ripgrep command timed out") from exc

        if completed.returncode not in (0, 1):
            raise ToolExecutionError(
                f"ripgrep failed with exit code {completed.returncode}: {completed.stderr.strip()}"
            )

        snippet = completed.stdout.strip() or "No matches found"
        return [
            RetrievalResult(
                file_path=root,
                start_line=1,
                end_line=len(snippet.splitlines()),
                code_snippet=snippet,
                confidence=0.25,
                notes=f"ripgrep search results for pattern '{pattern}'",
            )
        ]
