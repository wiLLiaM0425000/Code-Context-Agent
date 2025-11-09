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

3. Provide OpenAI credentials either via environment variables or CLI
   arguments when you want the planner to call the API. Supported variables
   include:
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL`
   - `OPENAI_MODEL`
   - `OPENAI_ORGANIZATION`

4. Extend the `Planner` and tool implementations to hook in your LLM provider
   and local analysis services as needed.

## Command Line Runner

The repository ships with a Typer-based CLI that mirrors the agent's core
contract, making it easy to experiment against local projects:

```bash
context-agent run \
  /path/to/workspace \
  src/module.py \
  10 40 \
  --symbol TargetClass \
  --intent symbol_definition \
  --query "Locate the definition of TargetClass" \
  --openai-api-key "$OPENAI_API_KEY"
```

The CLI resolves relative file paths against the workspace, executes the
retrieval pipeline, and prints the final request/response payload as JSON for
easy inspection.

## MCP Tool Integration

To expose the agent as a Model Context Protocol (MCP) tool, install the
optional `modelcontextprotocol` package and launch the stdio server:

```bash
pip install -e .[mcp]
python -m context_agent.integrations.mcp
```

This registers a `retrieve_code_context` MCP tool that accepts the same
arguments as the CLI. Host applications can import and use
`context_agent.integrations.create_mcp_server` to embed the tool directly.

## Documentation

- [Workflow Flowchart](docs/context_agent_flowchart.md)
- [Project Structure](docs/project_structure.md)
