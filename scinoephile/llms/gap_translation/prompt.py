#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for gap translation matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["GapTranslationPrompt"]


class GapTranslationPrompt(Prompt, ABC):
    """Text for LLM correspondence for gap translation matters."""

    # Query fields
    src_1_pfx: ClassVar[str] = "one_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "Subtitle {idx} text from source one"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "two_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "Subtitle {idx} text from source two"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = 'Subtitle {idx} output, or "" if no change.'
    """Description template for output fields in answer."""

    # Query fields
    @classmethod
    def src_1(cls, idx: int) -> str:
        """Name of source one field in query."""
        return f"{cls.src_1_pfx}{idx}"

    @classmethod
    def src_1_desc(cls, idx: int) -> str:
        """Description of source one field in query."""
        return cls.src_1_desc_tpl.format(idx=idx)

    @classmethod
    def src_2(cls, idx: int) -> str:
        """Name of source two field in query."""
        return f"{cls.src_2_pfx}{idx}"

    @classmethod
    def src_2_desc(cls, idx: int) -> str:
        """Description of source two field in query."""
        return cls.src_2_desc_tpl.format(idx=idx)

    # Answer fields
    @classmethod
    def output_contains_note_err(cls, idx: int) -> str:
        """Error when output includes note-like text."""
        template = getattr(cls, "output_contains_note_err_tpl")
        return str(template).format(idx=idx)

    @classmethod
    def output(cls, idx: int) -> str:
        """Name of output field in answer."""
        return f"{cls.output_pfx}{idx}"

    @classmethod
    def output_desc(cls, idx: int) -> str:
        """Description of output subtitle field in answer."""
        return cls.output_desc_tpl.format(idx=idx)
