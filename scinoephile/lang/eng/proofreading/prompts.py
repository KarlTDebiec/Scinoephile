#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.blockwise import BlockwisePrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.eng.prompts import EngPrompt

__all__ = ["EngProofreadingPrompt"]


class EngProofreadingPrompt(BlockwisePrompt, EngPrompt):
    """LLM correspondence text for English proofreading."""

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

    input_prefix: ClassVar[str] = "subtitle_"
    """Prefix for input fields in query."""

    input_description_template: ClassVar[str] = "Subtitle {idx}"
    """Description template for input fields in query."""

    output_prefix: ClassVar[str] = "revised_"
    """Prefix for output fields in answer."""

    output_description_template: ClassVar[str] = (
        "Subtitle {idx} revised, or an empty string if no revision is necessary."
    )
    """Description template for output fields in answer."""

    note_description_template: ClassVar[str] = (
        "Note concerning revisions to subtitle {idx}, or an empty string if no "
        "revision is necessary."
    )
    """Description template for note fields in answer."""

    output_unmodified_error_template: ClassVar[str] = (
        "Answer's revised text {idx} is not modified relative to query's text {idx}, "
        "if no revision is needed an empty string must be provided."
    )
    """Error template when output is present but unmodified."""

    note_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is modified relative to query's text {idx}, but no note "
        "is provided, if revision is needed a note must be provided."
    )
    """Error template when note is missing for a change."""

    output_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is not modified relative to query's text {idx}, but a "
        "note is provided, if no revisions are needed an empty string must be provided."
    )
    """Error template when output is missing for a note."""
