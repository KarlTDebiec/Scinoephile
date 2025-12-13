#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base prompt text for proofreading."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["ProofreadingPrompt"]


class ProofreadingPrompt(Prompt, ABC):
    """Base prompt text for proofreading."""

    subtitle_prefix: ClassVar[str] = "subtitle_"
    """Prefix of subtitle field in query."""

    subtitle_description_template: ClassVar[str] = "Subtitle {idx}"
    """Description template for subtitle field in query."""

    revised_prefix: ClassVar[str] = "revised_"
    """Prefix of revised subtitle field in answer."""

    revised_description_template: ClassVar[str] = (
        "Subtitle {idx} revised, or an empty string if no revision is necessary."
    )
    """Description template for revised subtitle field in answer."""

    note_prefix: ClassVar[str] = "note_"
    """Prefix of note field in answer."""

    note_description_template: ClassVar[str] = (
        "Note concerning revisions to subtitle {idx}, or an empty string if no "
        "revision is necessary."
    )
    """Description template for note field in answer."""

    subtitle_revised_equal_error_template: ClassVar[str] = (
        "Answer's revised text {idx} is not modified relative to query's text {idx}, "
        "if no revision is needed an empty string must be provided."
    )
    """Error template when subtitle and revised fields are equal."""

    note_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is modified relative to query's text {idx}, but no note "
        "is provided, if revision is needed a note must be provided."
    )
    """Error template when note is missing for a revision."""

    revised_missing_error_template: ClassVar[str] = (
        "Answer's text {idx} is not modified relative to query's text {idx}, but a "
        "note is provided, if no revisions are needed an empty string must be provided."
    )
    """Error template when revision is missing but note is provided."""

    @classmethod
    def subtitle_field(cls, idx: int) -> str:
        """Name of subtitle field in query."""
        return f"{cls.subtitle_prefix}{idx}"

    @classmethod
    def subtitle_description(cls, idx: int) -> str:
        """Description of subtitle field in query."""
        return cls.subtitle_description_template.format(idx=idx)

    @classmethod
    def revised_field(cls, idx: int) -> str:
        """Name of revised subtitle field in answer."""
        return f"{cls.revised_prefix}{idx}"

    @classmethod
    def revised_description(cls, idx: int) -> str:
        """Description of revised subtitle field in answer."""
        return cls.revised_description_template.format(idx=idx)

    @classmethod
    def note_field(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"{cls.note_prefix}{idx}"

    @classmethod
    def note_description(cls, idx: int) -> str:
        """Description of note field in answer."""
        return cls.note_description_template.format(idx=idx)

    @classmethod
    def subtitle_revised_equal_error(cls, idx: int) -> str:
        """Error message when subtitle and revised fields are equal."""
        return cls.subtitle_revised_equal_error_template.format(idx=idx)

    @classmethod
    def note_missing_error(cls, idx: int) -> str:
        """Error message when note is missing for a revision."""
        return cls.note_missing_error_template.format(idx=idx)

    @classmethod
    def revised_missing_error(cls, idx: int) -> str:
        """Error message when revision is missing but note is provided."""
        return cls.revised_missing_error_template.format(idx=idx)
