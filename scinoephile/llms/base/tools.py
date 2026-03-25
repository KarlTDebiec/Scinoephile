#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tool-related types for LLM interactions."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any, TypedDict

__all__ = ["LLMToolSpec", "ToolHandler"]


class LLMToolSpec(TypedDict):
    """Specification for one LLM-callable function tool."""

    name: str
    description: str
    parameters: dict[str, object]


type ToolHandler = Callable[[dict[str, Any]], object | Awaitable[object]]
"""Function that executes one tool call from parsed JSON arguments."""
