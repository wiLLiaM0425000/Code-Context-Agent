# Code Context Agent

This repository provides a reference implementation for a stateless LLM agent
that retrieves contextual information for codebases in languages such as Java,
Python, C/C++, Go, JavaScript, and TypeScript. The agent orchestrates an LLM
planner with a collection of deterministic tools to surface code snippets that
answer user questions about symbols, values, or related logic.

## Features

- **Planner-first workflow** that lets an LLM decide which tools to run for a
  particular retrieval intent.
- **Extensible tool registry** with stubs for directory exploration, symbol
  indexing, file reading, ripgrep search, and result submission.
- **Python package layout** ready for integration into CLI, API, or serverless
  deployments.

## Getting Started

1. Install dependencies:
   ```bash
   pip install -e .[dev]
   ```
2. Integrate the package:
   ```python
   from pathlib import Path

   from context_agent import create_app
   from context_agent.models import RetrievalIntent, RetrievalRequest

   agent = create_app()
   request = RetrievalRequest(
       workspace_path=Path("/path/to/project"),
       file_path=Path("src/main.py"),
       start_line=10,
       end_line=30,
       symbol="main",
       intent=RetrievalIntent.SYMBOL_IMPLEMENTATION,
       natural_language_query="Find the implementation of main",
   )
   results = list(agent.run(request))
   ```

3. Extend the `Planner` and tool implementations to hook in your LLM provider
   and local analysis services.

## Documentation

- [Workflow Flowchart](docs/context_agent_flowchart.md)
- [Project Structure](docs/project_structure.md)
