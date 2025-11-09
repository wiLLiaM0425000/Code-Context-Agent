"""Tool for listing directory structure within the workspace."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from ..models import RetrievalRequest, RetrievalResult
from .base import BaseTool


class DirectoryTreeTool(BaseTool):
    """Produce a textual representation of the project directory tree."""

    def execute(self, request: RetrievalRequest, **kwargs) -> Iterable[RetrievalResult]:
        root = request.workspace_path
        tree = self._build_tree(root=root)
        return [
            RetrievalResult(
                file_path=root,
                start_line=1,
                end_line=len(tree.splitlines()) if tree else 0,
                code_snippet=tree or "(empty directory)",
                confidence=0.2,
                notes="Workspace directory tree",
            )
        ]

    def _build_tree(self, root: Path, indent: str = "") -> str:
        entries: List[str] = []
        for path in sorted(root.iterdir()):
            if path.name.startswith("."):
                continue
            entries.append(f"{indent}- {path.name}")
            if path.is_dir():
                nested = self._build_tree(path, indent + "  ")
                if nested:
                    entries.append(nested)
        return "\n".join(entries)
