#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for mono track / subtitle block matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.base import Prompt

__all__ = ["MonoBlockPrompt"]


class MonoBlockPrompt(Prompt, ABC):
    """Text for LLM correspondence for mono track / subtitle block matters."""

    # Query fields
    input_pfx: ClassVar[str] = "input_"
    """Prefix for input fields in query."""

    input_desc_tpl: ClassVar[str] = "Input {idx}"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        "Output {idx}, or an empty string if no change is necessary."
    )
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "note_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = (
        "Note concerning output {idx}, or an empty string if no change is necessary."
    )
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "Answer's output {idx} is unmodified relative to query's input {idx}, "
        "if no change is needed an empty string must be provided."
    )
    """Error template when output is present but unmodified."""

    note_missing_err_tpl: ClassVar[str] = (
        "Answer's output {idx} is modified relative to query's input {idx}, but no "
        "note is provided, if a change is needed a note must be provided."
    )
    """Error template when note is missing for a change."""

    output_missing_err_tpl: ClassVar[str] = (
        "Answer's output {idx} is not provided relative to query's input {idx}, but a "
        "note is provided, if no change is needed an empty string must be provided."
    )
    """Error template when output is missing for a note."""

    # Query fields
    @classmethod
    def input(cls, idx: int) -> str:
        """Name of input field in query."""
        return f"{cls.input_pfx}{idx}"

    @classmethod
    def input_desc(cls, idx: int) -> str:
        """Description of input field in query."""
        return cls.input_desc_tpl.format(idx=idx)

    # Answer fields
    @classmethod
    def output(cls, idx: int) -> str:
        """Name of output field in answer."""
        return f"{cls.output_pfx}{idx}"

    @classmethod
    def output_desc(cls, idx: int) -> str:
        """Description of output field in answer."""
        return cls.output_desc_tpl.format(idx=idx)

    @classmethod
    def note(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"{cls.note_pfx}{idx}"

    @classmethod
    def note_desc(cls, idx: int) -> str:
        """Description of note field in answer."""
        return cls.note_desc_tpl.format(idx=idx)

    # Test case errors
    @classmethod
    def output_unmodified_err(cls, idx: int) -> str:
        """Error when output is present but unmodified.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return cls.output_unmodified_err_tpl.format(idx=idx)

    @classmethod
    def note_missing_err(cls, idx: int) -> str:
        """Error when note is missing for a change.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return cls.note_missing_err_tpl.format(idx=idx)

    @classmethod
    def output_missing_err(cls, idx: int) -> str:
        """Error when output is missing for a note.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return cls.output_missing_err_tpl.format(idx=idx)
