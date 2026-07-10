#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for gap translation matters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["GapTranslationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class GapTranslationPrompt(Prompt):
    """Text for LLM correspondence for gap translation matters."""

    # Query fields
    src_1_pfx: str = "one_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: str = "Subtitle {idx} text from source one"
    """Description template for source one fields in query."""

    src_2_pfx: str = "two_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: str = "Subtitle {idx} text from source two"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: str = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: str = 'Subtitle {idx} output, or "" if no change.'
    """Description template for output fields in answer."""

    # Answer validation errors
    output_contains_note_err_tpl: str = ""
    """Error template when output includes note-like text."""
    output_unmodified_err_tpl: str = ""
    """Error template when output is unchanged."""

    # Dictionary tool
    dictionary_tool_name: str = ""
    """Name of dictionary lookup tool."""
    dictionary_tool_description: str = ""
    """Description of dictionary lookup tool."""
    dictionary_tool_query_description: str = ""
    """Description of dictionary lookup query."""

    # Query fields
    def src_1(self, idx: int) -> str:
        """Name of source one field in query."""
        return f"{self.src_1_pfx}{idx}"

    def src_1_desc(self, idx: int) -> str:
        """Description of source one field in query."""
        return self.src_1_desc_tpl.format(idx=idx)

    def src_2(self, idx: int) -> str:
        """Name of source two field in query."""
        return f"{self.src_2_pfx}{idx}"

    def src_2_desc(self, idx: int) -> str:
        """Description of source two field in query."""
        return self.src_2_desc_tpl.format(idx=idx)

    # Answer fields
    def output_contains_note_err(self, idx: int) -> str:
        """Error when output includes note-like text."""
        return self.output_contains_note_err_tpl.format(idx=idx)

    def output(self, idx: int) -> str:
        """Name of output field in answer."""
        return f"{self.output_pfx}{idx}"

    def output_desc(self, idx: int) -> str:
        """Description of output subtitle field in answer."""
        return self.output_desc_tpl.format(idx=idx)
