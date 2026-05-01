#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tool-related types for LLM interactions."""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from typing import Any, cast

__all__ = [
    "Tool",
    "ToolBox",
]


@dataclass(frozen=True)
class Tool:
    """One LLM-callable tool definition and its local handler."""

    spec: dict[str, object]
    """Tool schema exposed to the model."""

    handler: Callable[[dict[str, Any]], object]
    """Local handler for executing the tool."""

    @property
    def name(self) -> str:
        """Tool name."""
        return cast(str, self.spec["name"])


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
