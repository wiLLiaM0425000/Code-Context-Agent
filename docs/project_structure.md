# Project Structure

This document captures the canonical layout for the stateless code context
retrieval agent. The structure is language-agnostic for the target projects the
agent will inspect, while the agent itself is implemented in Python.

```
Code-Context-Agent/
├── docs/
│   ├── context_agent_flowchart.md   # High-level workflow diagram
│   └── project_structure.md         # Architecture and module overview
├── pyproject.toml                   # Build metadata and dependencies
├── README.md                        # Getting started guide
└── src/
    └── context_agent/
        ├── __init__.py              # Package exports
        ├── app.py                   # Factory for wiring the agent
        ├── config.py                # Runtime configuration dataclasses
        ├── models.py                # Core domain models and plan types
        ├── pipeline.py              # Planner + tool execution orchestration
        ├── planner.py               # LLM planner (OpenAI-aware with fallback)
        ├── tool_registry.py         # Registry for available tools
        ├── cli.py                   # Typer CLI for local experimentation
        ├── integrations/
        │   ├── __init__.py          # Integration exports
        │   └── mcp.py               # Model Context Protocol (MCP) adapter
        └── tools/
            ├── __init__.py          # (optional) namespace exports
            ├── base.py              # Shared tool abstractions
            ├── directory_tree.py    # Workspace tree inspection tool
            ├── file_reader.py       # File segment reader tool
            ├── report.py            # Submission helper tool
            ├── ripgrep.py           # Keyword search integration
            └── symbol_index.py      # Static analysis metadata tool
```

The package is designed for extension:

- **`Planner`**: encapsulates prompt engineering and LLM interaction needed to
  decide which tools should run. Additional strategies (e.g., feedback loops,
  retries) can be added without modifying downstream code.
- **`RetrievalPipeline`**: executes each plan step in sequence, enabling richer
  control flow such as branching or result aggregation in future iterations.
- **`Tool` implementations**: wrap concrete capabilities. Each tool receives the
  full `RetrievalRequest` plus tool-specific arguments, allowing contextual
  awareness while remaining deterministic.

Future work can flesh out the current stubs with production implementations,
including OpenAI client calls, AST parsing utilities, streaming responses, and
observability hooks.
