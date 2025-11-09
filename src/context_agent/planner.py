"""LLM-powered planner that determines which tools to run."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from typing import Any, Dict, List, Optional

from .config import AgentConfig
from .models import Plan, PlanStep, RetrievalIntent, RetrievalRequest


@dataclass
class Planner:
    """Orchestrates plan generation by delegating to the LLM."""

    config: AgentConfig
    _client: Optional["OpenAI"] = None

    def __post_init__(self) -> None:
        if self.config.openai_api_key:
            try:
                from openai import OpenAI

                self._client = OpenAI(
                    api_key=self.config.openai_api_key,
                    base_url=self.config.openai_base_url,
                    organization=self.config.openai_organization,
                )
            except Exception:  # pragma: no cover - runtime dependency guard
                logging.getLogger(__name__).exception("Failed to initialise OpenAI client; falling back to heuristic planner")
                self._client = None

    def create_plan(self, request: RetrievalRequest) -> Plan:
        """Create a plan stub based on the request intent.

        In a full implementation this method would call the LLM to propose
        tool invocations. For now we generate a deterministic scaffold to
        illustrate the orchestration flow.
        """

        if self._client:
            plan = self._plan_with_llm(request)
            if plan:
                return plan

        return self._heuristic_plan(request)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _heuristic_plan(self, request: RetrievalRequest) -> Plan:
        if request.intent == RetrievalIntent.SYMBOL_IMPLEMENTATION:
            steps = [
                PlanStep(
                    description="Find implementations of the target symbol",
                    tool_name="symbol_index",
                    arguments={"symbol": request.symbol},
                )
            ]
        elif request.intent == RetrievalIntent.SYMBOL_REFERENCES:
            steps = [
                PlanStep(
                    description="Search for references to the symbol",
                    tool_name="ripgrep",
                    arguments={"pattern": request.symbol},
                )
            ]
        else:
            steps = [
                PlanStep(
                    description="Read the relevant file segment",
                    tool_name="file_reader",
                    arguments={
                        "file_path": request.file_path,
                        "start_line": request.start_line,
                        "end_line": request.end_line,
                    },
                )
            ]

        steps.append(
            PlanStep(
                description="Submit collated retrieval results",
                tool_name="submit_result",
                arguments={},
            )
        )

        return Plan(steps=steps)

    def _plan_with_llm(self, request: RetrievalRequest) -> Optional[Plan]:
        assert self._client is not None

        prompt = self._build_prompt(request)
        try:
            response_text = self._ask_llm(prompt)
        except Exception:  # pragma: no cover - network failure guard
            logging.getLogger(__name__).exception("LLM planning failed; using heuristic fallback")
            return None

        try:
            payload = self._extract_json(response_text)
        except ValueError:
            logging.getLogger(__name__).warning("LLM response was not valid JSON. Falling back to heuristic plan")
            return None

        steps: List[PlanStep] = []
        for entry in payload.get("steps", []):
            tool_name = entry.get("tool")
            if not tool_name:
                continue
            arguments = entry.get("arguments") or {}
            if tool_name == "submit_result":
                arguments = {}

            description = entry.get("description") or f"Execute tool {tool_name}"
            steps.append(
                PlanStep(
                    description=description,
                    tool_name=tool_name,
                    arguments=arguments,
                )
            )

        if not steps:
            return None

        if steps[-1].tool_name != "submit_result":
            steps.append(
                PlanStep(
                    description="Submit collated retrieval results",
                    tool_name="submit_result",
                    arguments={},
                )
            )

        return Plan(steps=steps)

    def _build_prompt(self, request: RetrievalRequest) -> str:
        available_tools = [
            "directory_tree",
            "symbol_index",
            "file_reader",
            "ripgrep",
            "submit_result",
        ]
        description = {
            "symbol_implementation": "Identify implementations of a symbol",
            "symbol_references": "Find where the symbol is referenced",
            "symbol_definition": "Read the definition of the symbol",
            "value_lookup": "Lookup the value assigned to a name",
            "related_context": "Gather surrounding code context",
        }

        prompt = (
            "You are a planner that selects which tools a code context retrieval "
            "agent should run. You must respond with JSON containing a 'steps' "
            "array. Each item has fields: tool (one of "
            + ", ".join(available_tools)
            + "), description, and arguments (object).\n\n"
            "Request details:\n"
            f"- Workspace: {request.workspace_path}\n"
            f"- File: {request.file_path}\n"
            f"- Lines: {request.start_line}-{request.end_line}\n"
            f"- Symbol: {request.symbol}\n"
            f"- Intent: {request.intent.value} ({description.get(request.intent.value, '')})\n"
            f"- Natural language query: {request.natural_language_query or 'N/A'}\n"
        )

        return prompt

    def _ask_llm(self, prompt: str) -> str:
        assert self._client is not None
        # Prefer the Responses API, fall back to Chat Completions if unavailable.
        if hasattr(self._client, "responses"):
            response = self._client.responses.create(
                model=self.config.model,
                input=[
                    {"role": "system", "content": "Return only valid JSON without commentary."},
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.temperature,
            )
            text = getattr(response, "output_text", None)
            if text:
                return text

            output = getattr(response, "output", None)
            if output:
                segments = []
                for item in output:
                    content = item.get("content") if isinstance(item, dict) else getattr(item, "content", None)
                    if not content:
                        continue
                    for fragment in content:
                        fragment_text = fragment.get("text") if isinstance(fragment, dict) else getattr(fragment, "text", "")
                        if fragment_text:
                            segments.append(fragment_text)
                if segments:
                    return "".join(segments)

        # Fallback for Chat Completions style clients
        completion = self._client.chat.completions.create(  # type: ignore[attr-defined]
            model=self.config.model,
            messages=[
                {"role": "system", "content": "Return only valid JSON without commentary."},
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.temperature,
        )
        choice = completion.choices[0]
        message = getattr(choice, "message", None)
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "".join(
                    fragment.get("text", "") if isinstance(fragment, dict) else str(fragment)
                    for fragment in content
                )

        content = getattr(choice, "content", None)
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                fragment.get("text", "") if isinstance(fragment, dict) else str(fragment)
                for fragment in content
            )
        return ""

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "json" in text[:10].lower():
                text = text.split("\n", 1)[-1]
        if "```" in text:
            text = text.split("```", 1)[0]

        return json.loads(text)
