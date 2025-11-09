"""Tool for final aggregation and submission of retrieval results."""

from __future__ import annotations

from typing import Iterable, List

from ..models import RetrievalRequest, RetrievalResult
from .base import BaseTool


class SubmitResultTool(BaseTool):
    """Finalize the retrieval results."""

    def execute(self, request: RetrievalRequest, **kwargs) -> Iterable[RetrievalResult]:
        results: List[RetrievalResult] = kwargs.get("results", [])
        # In the reference implementation this would call the submission API.
        summary = "\n".join(
            f"{result.file_path}:{result.start_line}-{result.end_line} | {result.confidence}"
            for result in results
        )
        return [
            RetrievalResult(
                file_path=request.file_path,
                start_line=request.start_line,
                end_line=request.end_line,
                code_snippet=summary or "No results to submit",
                confidence=1.0,
                notes="Submission payload prepared",
            )
        ]
