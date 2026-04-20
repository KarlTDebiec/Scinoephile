#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Protocol for prompt-provided dictionary tool specification text."""

from __future__ import annotations

from typing import ClassVar, Protocol

__all__ = [
    "DictionaryToolPrompt",
]


class DictionaryToolPrompt(Protocol):
    """Prompt text required to build dictionary tool specifications."""

    dictionary_tool_name: ClassVar[str]
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str]
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str]
    """Description of the dictionary lookup query parameter."""
