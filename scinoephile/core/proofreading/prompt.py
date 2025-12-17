#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM correspondence text for proofreading."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["ProofreadingPrompt"]


class ProofreadingPrompt(Prompt, ABC):
    """ABC for LLM correspondence text for proofreading."""

    # Query fields
    subtitle_prefix: ClassVar[str] = "subtitle_"
    """Prefix for subtitle fields in query."""

    @classmethod
    def subtitle_field(cls, idx: int) -> str:
        """Name of subtitle field in query."""
        return f"{cls.subtitle_prefix}{idx}"

    subtitle_description_template: ClassVar[str] = "Subtitle {idx}"
    """Description template for subtitle fields in query."""

    @classmethod
    def subtitle_description(cls, idx: int) -> str:
        """Description of subtitle field in query."""
        return cls.subtitle_description_template.format(idx=idx)

    # Answer fields
    revised_prefix: ClassVar[str] = "revised_"
    """Prefix for revised fields in answer."""

    @classmethod
    def revised_field(cls, idx: int) -> str:
        """Name of revised field in answer."""
        return f"{cls.revised_prefix}{idx}"

    revised_description_template: ClassVar[str] = (
        "Subtitle {idx} revised, or an empty string if no revision is necessary."
    )
    """Description template for revised fields in answer."""

    @classmethod
    def revised_description(cls, idx: int) -> str:
        """Description of revised subtitle field in answer."""
        return cls.revised_description_template.format(idx=idx)

    note_prefix: ClassVar[str] = "note_"
    """Prefix of note fields in answer."""

    @classmethod
    def note_field(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"{cls.note_prefix}{idx}"

    note_description_template: ClassVar[str] = (
        "Note concerning revisions to subtitle {idx}, or an empty string if no "
        "revision is necessary."
    )
    """Description template for note fields in answer."""

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
        """Error when subtitle and revised fields are equal.

        Arguments:
            idx: index of subtitle
        Returns:
            error message
        """
        return cls.subtitle_revised_equal_error_template.format(idx=idx)

    note_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is modified relative to query's text {idx}, but no note "
        "is provided, if revision is needed a note must be provided."
    )
    """Error template when note is missing for a revision."""

    @classmethod
    def note_missing_error(cls, idx: int) -> str:
        """Error when note is missing for a revision.

        Arguments:
            idx: index of subtitle
        Returns:
            error message
        """
        return cls.note_missing_error_template.format(idx=idx)

    revised_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is not modified relative to query's text {idx}, but a "
        "note is provided, if no revisions are needed an empty string must be provided."
    )
    """Error template when revision is missing for a note."""

    @classmethod
    def revised_missing_error(cls, idx: int) -> str:
        """Error when revision is missing for a note.

        Arguments:
            idx: index of subtitle
        Returns:
            error message
        """
        return cls.revised_missing_error_template.format(idx=idx)
