#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for review matters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["ReviewPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewPrompt(Prompt):
    """Text for LLM correspondence for review matters."""

    # Query fields
    input_pfx: str = "subtitle_"
    """Prefix for input fields in query."""

    input_desc_tpl: str = "Input {idx}"
    """Description template for input fields in query."""

    # Answer fields
    output_pfx: str = "revised_"
    """Prefix for output fields in answer."""

    output_desc_tpl: str = "Output {idx}, or an empty string if no change is necessary."
    """Description template for output fields in answer."""

    note_pfx: str = "note_"
    """Prefix for note fields in answer."""

    note_desc_tpl: str = (
        "Note concerning output {idx}, or an empty string if no change is necessary."
    )
    """Description template for note fields in answer."""

    # Test case errors
    output_unmodified_err_tpl: str = (
        "Answer's output {idx} is unmodified relative to query's input {idx}, "
        "if no change is needed an empty string must be provided."
    )
    """Error template when output is present but unmodified."""

    note_missing_err_tpl: str = (
        "Answer's output {idx} is modified relative to query's input {idx}, but no "
        "note is provided, if a change is needed a note must be provided."
    )
    """Error template when note is missing for a change."""

    output_missing_err_tpl: str = (
        "Answer's output {idx} is not provided relative to query's input {idx}, but a "
        "note is provided, if no change is needed an empty string must be provided."
    )
    """Error template when output is missing for a note."""

    # Query fields
    def input(self, idx: int) -> str:
        """Name of input field in query."""
        return f"{self.input_pfx}{idx}"

    def input_desc(self, idx: int) -> str:
        """Description of input field in query."""
        return self.input_desc_tpl.format(idx=idx)

    # Answer fields
    def note(self, idx: int) -> str:
        """Name of note field in answer."""
        return f"{self.note_pfx}{idx}"

    def note_desc(self, idx: int) -> str:
        """Description of note field in answer."""
        return self.note_desc_tpl.format(idx=idx)

    def output(self, idx: int) -> str:
        """Name of output field in answer."""
        return f"{self.output_pfx}{idx}"

    def output_desc(self, idx: int) -> str:
        """Description of output field in answer."""
        return self.output_desc_tpl.format(idx=idx)

    # Test case errors
    def note_missing_err(self, idx: int) -> str:
        """Error when note is missing for a change.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return self.note_missing_err_tpl.format(idx=idx)

    def output_missing_err(self, idx: int) -> str:
        """Error when output is missing for a note.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return self.output_missing_err_tpl.format(idx=idx)

    def output_unmodified_err(self, idx: int) -> str:
        """Error when output is present but unmodified.

        Arguments:
            idx: index of item
        Returns:
            error message
        """
        return self.output_unmodified_err_tpl.format(idx=idx)
