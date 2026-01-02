#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for dual track / subtitle block matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.base import Prompt

__all__ = ["DualBlockPrompt"]


class DualBlockPrompt(Prompt, ABC):
    """Text for LLM correspondence for dual track / subtitle block matters."""

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

    note_pfx: ClassVar[str] = "note_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = 'Subtitle {idx} output note, or "" if no change.'
    """Description template for note fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "Answer's output {idx} is unmodified relative to query's source one {idx}, "
        'if no change, "" must be present.'
    )
    """Error template when output is present but unmodified relative to source one."""

    output_missing_note_present_err_tpl: ClassVar[str] = (
        "Answer's output {idx} is unmodified relative to query's source one {idx}, "
        'but a note is present, if output is "" no note may be present.'
    )
    """Error template when output is missing but note is present."""

    output_present_note_missing_err_tpl: ClassVar[str] = (
        "Answer's output {idx} is modified relative to query's source one {idx}, "
        "but no note is present, if output is present note must be present."
    )
    """Error template when output is present but note is missing."""

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
    def output(cls, idx: int) -> str:
        """Name of output field in answer."""
        return f"{cls.output_pfx}{idx}"

    @classmethod
    def output_desc(cls, idx: int) -> str:
        """Description of output subtitle field in answer."""
        return cls.output_desc_tpl.format(idx=idx)

    @classmethod
    def note(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"{cls.note_pfx}{idx}"

    @classmethod
    def note_desc(cls, idx: int) -> str:
        """Description of note field in answer."""
        return cls.note_desc_tpl.format(idx=idx)

    # Test case validation errors
    @classmethod
    def output_present_but_unmodified_err(cls, idx: int) -> str:
        """Error when output is present but unmodified relative to source one.

        Arguments:
            idx: index of subtitle
        Returns:
            error message
        """
        return cls.output_unmodified_err_tpl.format(idx=idx)

    @classmethod
    def output_missing_note_present_err(cls, idx: int) -> str:
        """Error when output is missing but note is present.

        Arguments:
            idx: index of subtitle
        Returns:
            error message
        """
        return cls.output_missing_note_present_err_tpl.format(idx=idx)

    @classmethod
    def output_present_note_missing_err(cls, idx: int) -> str:
        """Error when output is present but note is missing.

        Arguments:
            idx: index of subtitle
        Returns:
            error message
        """
        return cls.output_present_note_missing_err_tpl.format(idx=idx)
