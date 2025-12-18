#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM correspondence text for mono track / block processing."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.base import Prompt

__all__ = ["MonoBlockPrompt"]


class MonoBlockPrompt(Prompt, ABC):
    """ABC for LLM correspondence text for mono track / block processing."""

    # Query fields
    input_prefix: ClassVar[str] = "input_"
    """Prefix for input fields in query."""

    input_description_template: ClassVar[str] = "Input {idx}"
    """Description template for input fields in query."""

    # Answer fields
    output_prefix: ClassVar[str] = "output_"
    """Prefix for output fields in answer."""

    output_description_template: ClassVar[str] = (
        "Output {idx}, or an empty string if no change is necessary."
    )
    """Description template for output fields in answer."""

    note_prefix: ClassVar[str] = "note_"
    """Prefix for note fields in answer."""

    note_description_template: ClassVar[str] = (
        "Note concerning output {idx}, or an empty string if no change is necessary."
    )
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_error_template: ClassVar[str] = (
        "Answer's output {idx} is unmodified relative to query's input {idx}, "
        "if no change is needed an empty string must be provided."
    )
    """Error template when output is present but unmodified."""

    note_missing_error_template: ClassVar[str] = (
        "Answer's output {idx} is modified relative to query's input {idx}, but no "
        "note is provided, if a change is needed a note must be provided."
    )
    """Error template when note is missing for a change."""

    output_missing_error_template: ClassVar[str] = (
        "Answer's output {idx} is not provided relative to query's input {idx}, but a "
        "note is provided, if no change is needed an empty string must be provided."
    )
    """Error template when output is missing for a note."""

    # Query fields
    @classmethod
    def input_field(cls, idx: int) -> str:
        """Name of input field in query."""
        return f"{cls.input_prefix}{idx}"

    @classmethod
    def input_description(cls, idx: int) -> str:
        """Description of input field in query."""
        return cls.input_description_template.format(idx=idx)

    # Answer fields
    @classmethod
    def output_field(cls, idx: int) -> str:
        """Name of output field in answer."""
        return f"{cls.output_prefix}{idx}"

    @classmethod
    def output_description(cls, idx: int) -> str:
        """Description of output field in answer."""
        return cls.output_description_template.format(idx=idx)

    @classmethod
    def note_field(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"{cls.note_prefix}{idx}"

    @classmethod
    def note_description(cls, idx: int) -> str:
        """Description of note field in answer."""
        return cls.note_description_template.format(idx=idx)

    # Test case errors
    @classmethod
    def output_unmodified_error(cls, idx: int) -> str:
        """Error when output is present but unmodified.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return cls.output_unmodified_error_template.format(idx=idx)

    @classmethod
    def note_missing_error(cls, idx: int) -> str:
        """Error when note is missing for a change.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return cls.note_missing_error_template.format(idx=idx)

    @classmethod
    def output_missing_error(cls, idx: int) -> str:
        """Error when output is missing for a note.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return cls.output_missing_error_template.format(idx=idx)
