#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Collection of LLM-callable tools."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator
from typing import Any

from .tool import Tool

__all__ = ["ToolBox"]


class ToolBox:
    """Collection of LLM-callable tools."""

    def __init__(self, tools: Iterable[Tool] = ()):
        """Initialize.

        Arguments:
            tools: tools to include in this tool box
        """
        self._tools_by_name: dict[str, Tool] = {}
        for tool in tools:
            self.add(tool)

    def __bool__(self) -> bool:
        """Return whether this tool box contains any tools."""
        return bool(self._tools_by_name)

    def __iter__(self) -> Iterator[Tool]:
        """Iterate over contained tools."""
        return iter(self._tools_by_name.values())

    @property
    def handler_names(self) -> list[str]:
        """Sorted list of configured tool handler names."""
        return sorted(self._tools_by_name)

    @property
    def specs(self) -> list[dict[str, object]]:
        """Deterministically ordered tool specs."""
        return [
            tool.spec
            for tool in sorted(
                self._tools_by_name.values(),
                key=lambda tool: json.dumps(
                    tool.spec,
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        ]

    def add(self, tool: Tool):
        """Add one tool.

        Arguments:
            tool: tool to add
        Raises:
            ValueError: tool name is already registered
        """
        if tool.name in self._tools_by_name:
            raise ValueError(f"Tool '{tool.name}' is already registered.")
        self._tools_by_name[tool.name] = tool

    def get_handler(self, tool_name: str) -> Callable[[dict[str, Any]], object] | None:
        """Get a handler by tool name.

        Arguments:
            tool_name: tool name to resolve
        Returns:
            matching handler if present
        """
        tool = self._tools_by_name.get(tool_name)
        if tool is None:
            return None
        return tool.handler

    def run(self, tool_name: str, raw_arguments: str) -> object:
        """Execute one tool from model-produced JSON arguments.

        Arguments:
            tool_name: requested tool name
            raw_arguments: JSON argument payload from model tool call
        Returns:
            tool result payload
        """
        handler = self.get_handler(tool_name)
        if handler is None:
            return {"error": f"Unsupported tool '{tool_name}'."}

        parsed_arguments = self._parse_arguments(
            tool_name=tool_name,
            raw_arguments=raw_arguments,
        )
        if isinstance(parsed_arguments, dict) and "error" in parsed_arguments:
            return parsed_arguments

        return handler(parsed_arguments)

    def to_json(self) -> str:
        """Return a deterministic JSON representation of configured tools."""
        if not self:
            return ""
        return json.dumps(
            {
                "handler_names": self.handler_names,
                "tools": self.specs,
            },
            ensure_ascii=False,
            sort_keys=True,
        )

    @staticmethod
    def serialize_result(result: object) -> str:
        """Serialize tool-call result for tool response message content.

        Arguments:
            result: tool execution result
        Returns:
            serialized JSON content
        """
        try:
            return json.dumps(result, ensure_ascii=False)
        except TypeError:
            return json.dumps({"result": str(result)}, ensure_ascii=False)

    @staticmethod
    def _parse_arguments(tool_name: str, raw_arguments: str) -> dict[str, Any]:
        """Parse tool arguments from model-produced JSON.

        Arguments:
            tool_name: requested tool name
            raw_arguments: JSON argument payload from model tool call
        Returns:
            parsed arguments, or an error payload
        """
        try:
            parsed_arguments = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError:
            return {"error": f"Tool '{tool_name}' arguments are not valid JSON."}

        if not isinstance(parsed_arguments, dict):
            return {
                "error": f"Tool '{tool_name}' arguments must decode to a JSON object."
            }

        return parsed_arguments
