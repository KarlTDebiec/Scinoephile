#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for English proofreading."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english import EnglishPrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text

__all__ = ["EnglishProofreadingPrompt"]


class EnglishProofreadingPrompt(EnglishPrompt):
    """Text for LLM correspondence for English proofreading."""

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
        return f"subtitle_{idx}"

    @classmethod
    def subtitle_description(cls, idx: int) -> str:
        """Description of subtitle field in query."""
        return f"Subtitle {idx}"

    # Answer field names and descriptions
    revised_prefix: ClassVar[str] = "revised_"
    """Prefix of revised subtitle field in answer."""

    @classmethod
    def revised_field(cls, idx: int) -> str:
        """Name of revised subtitle field in answer."""
        return f"revised_{idx}"

    @classmethod
    def revised_description(cls, idx: int) -> str:
        """Description of revised subtitle field in answer."""
        return (
            f"Subtitle {idx} revised, or an empty string if no revision is necessary."
        )

    note_prefix: ClassVar[str] = "note_"
    """Prefix of note field in answer."""

    @classmethod
    def note_field(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"note_{idx}"

    @classmethod
    def note_description(cls, idx: int) -> str:
        """Description of note field in answer."""
        return (
            f"Note concerning revisions to subtitle {idx}, or an empty string if no "
            "revision is necessary."
        )

    # Test case validation errors
    @classmethod
    def subtitle_revised_equal_error(cls, idx: int) -> str:
        """Error message when subtitle and revised fields are equal."""
        return (
            f"Answer's revised text {idx} is not modified relative to query's text "
            f"{idx}, if no revision is needed an empty string must be provided."
        )

    @classmethod
    def note_missing_error(cls, idx: int) -> str:
        """Error message when note is missing for a revision."""
        return (
            f"Answer's text {idx} is modified relative to query's text {idx}, but no "
            "note is provided, if revision is needed a note must be provided."
        )

    @classmethod
    def revised_missing_error(cls, idx: int) -> str:
        """Error message when revision is missing but note is provided."""
        return (
            f"Answer's text {idx} is not modified relative to query's text {idx}, but "
            "a note is provided, if no revisions are needed an empty string must be "
            "provided."
        )
