"""Tool for reading file content from the workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..models import RetrievalRequest, RetrievalResult
from .base import BaseTool


class FileReaderTool(BaseTool):
    """Return the requested file content segment."""

    def execute(self, request: RetrievalRequest, **kwargs) -> Iterable[RetrievalResult]:
        file_path = Path(kwargs.get("file_path", request.file_path))
        start_line = kwargs.get("start_line", request.start_line)
        end_line = kwargs.get("end_line", request.end_line)
        snippet = self._read_lines(file_path, start_line, end_line)
        return [
            RetrievalResult(
                file_path=file_path,
                start_line=start_line,
                end_line=end_line,
                code_snippet=snippet,
                confidence=0.3,
                notes="Requested file segment",
            )
        ]

    def _read_lines(self, file_path: Path, start_line: int, end_line: int) -> str:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()
        selected = lines[start_line - 1 : end_line]
        return "\n".join(selected)
