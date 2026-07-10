#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for translation matters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["TranslationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class TranslationPrompt(Prompt):
    """Text for LLM correspondence for translation matters."""

    # Query fields
    input_pfx: str = "input_"
    """Prefix for input fields in query."""

    input_desc_tpl: str = "Input {idx}"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: str = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: str = "Output {idx}"
    """Description template for output fields in answer."""

    # Dictionary tool
    dictionary_tool_name: str = ""
    """Name of dictionary lookup tool."""
    dictionary_tool_description: str = ""
    """Description of dictionary lookup tool."""
    dictionary_tool_query_description: str = ""
    """Description of dictionary lookup query."""

    # Query fields
    def input(self, idx: int) -> str:
        """Name of input field in query."""
        return f"{self.input_pfx}{idx}"

    def input_desc(self, idx: int) -> str:
        """Description of input field in query."""
        return self.input_desc_tpl.format(idx=idx)

    # Answer fields
    def output(self, idx: int) -> str:
        """Name of output field in answer."""
        return f"{self.output_pfx}{idx}"

    def output_desc(self, idx: int) -> str:
        """Description of output field in answer."""
        return self.output_desc_tpl.format(idx=idx)
