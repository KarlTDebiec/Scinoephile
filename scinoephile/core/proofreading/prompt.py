#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM correspondence text for proofreading."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text

__all__ = ["ProofreadingPrompt"]


class ProofreadingPrompt(Prompt, ABC):
    """ABC for LLM correspondence text for proofreading."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        You are responsible for proofreading English subtitles generated using OCR.
        For each subtitle, you are to provide revised subtitle only if revisions are
        necessary.
        If revisions are needed, return the full revised subtitle, and a note describing
        the changes made.
        If no revisions are needed, return an empty string for the revised subtitle and
        its note.
        Make changes only when necessary to correct errors clearly resulting from OCR.

        Do not add stylistic changes or improve phrasing.

        Do not change colloquialisms or dialect such as 'gonna' or 'wanna'.

        Do not change spelling from British to American English or vice versa.

        Do not remove subtitle markup such as italics ('{\\i1}' and '{\\i0}').

        Do not remove newlines ('\\n').""")
    """Base system prompt."""

    # Query fields
    subtitle_prefix: ClassVar[str] = "subtitle_"
    """Prefix of subtitle field in query."""

    @classmethod
    def subtitle_field(cls, idx: int) -> str:
        """Name of subtitle field in query."""
        return f"{cls.subtitle_prefix}{idx}"

    subtitle_description_template: ClassVar[str] = "Subtitle {idx}"
    """Description template for subtitle field in query."""

    @classmethod
    def subtitle_description(cls, idx: int) -> str:
        """Description of subtitle field in query."""
        return cls.subtitle_description_template.format(idx=idx)

    # Answer fields
    revised_prefix: ClassVar[str] = "revised_"
    """Prefix of revised field in answer."""

    @classmethod
    def revised_field(cls, idx: int) -> str:
        """Name of revised field in answer."""
        return f"{cls.revised_prefix}{idx}"

    revised_description_template: ClassVar[str] = (
        "Subtitle {idx} revised, or an empty string if no revision is necessary."
    )
    """Description template for revised  field in answer."""

    @classmethod
    def revised_description(cls, idx: int) -> str:
        """Description of revised subtitle field in answer."""
        return cls.revised_description_template.format(idx=idx)

    note_prefix: ClassVar[str] = "note_"
    """Prefix of note field in answer."""

    @classmethod
    def note_field(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"{cls.note_prefix}{idx}"

    note_description_template: ClassVar[str] = (
        "Note concerning revisions to subtitle {idx}, or an empty string if no "
        "revision is necessary."
    )
    """Description template for note field in answer."""

    @classmethod
    def note_description(cls, idx: int) -> str:
        """Description of note field in answer."""
        return cls.note_description_template.format(idx=idx)

    # Test case errors
    subtitle_revised_equal_error_template: ClassVar[str] = (
        "Answer's revised text {idx} is not modified relative to query's text {idx}, "
        "if no revision is needed an empty string must be provided."
    )
    """Error template when subtitle and revised fields are equal."""

    @classmethod
    def subtitle_revised_equal_error(cls, idx: int) -> str:
        """Error message when subtitle and revised fields are equal."""
        return cls.subtitle_revised_equal_error_template.format(idx=idx)

    note_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is modified relative to query's text {idx}, but no note "
        "is provided, if revision is needed a note must be provided."
    )
    """Error template when note is missing for a revision."""

    @classmethod
    def note_missing_error(cls, idx: int) -> str:
        """Error message when note is missing for a revision."""
        return cls.note_missing_error_template.format(idx=idx)

    revised_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is not modified relative to query's text {idx}, but a "
        "note is provided, if no revisions are needed an empty string must be provided."
    )
    """Error template when revision is missing for a note."""

    @classmethod
    def revised_missing_error(cls, idx: int) -> str:
        """Error message when revision is missing for a note."""
        return cls.revised_missing_error_template.format(idx=idx)
