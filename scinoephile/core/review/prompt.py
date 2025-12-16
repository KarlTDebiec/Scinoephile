#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription review."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = [
    "ReviewPrompt",
]


class ReviewPrompt(Prompt, ABC):
    """Text for LLM correspondence for 粤文 transcription review."""

    # Query fields
    source_one_field: ClassVar[str] = "one"
    """Field name for OCR source one."""

    source_one_description: ClassVar[str] = "Subtitle text from OCR source one"
    """Description of source one field."""

    source_two_field: ClassVar[str] = "two"
    """Field name for OCR source two."""

    source_two_description: ClassVar[str] = "Subtitle text from OCR source two"
    """Description of source two field."""

    # Answer fields
    fused_field: ClassVar[str] = "output"
    """Field name for fused subtitle text."""

    fused_description: ClassVar[str] = "Merged subtitle text"
    """Description of fused field."""

    note_field: ClassVar[str] = "note"
    """Field name for explanation of changes."""

    note_description: ClassVar[str] = "Explanation of changes made"
    """Description of note field."""

    # Test case validation errors
    yuewen_unmodified_error_template: ClassVar[str] = (
        "Answer's revised 粤文 text {idx} is not modified relative to query's 粤文 "
        "text {idx}, if no revision is needed an empty string must be provided."
    )
    """Error template when revised 粤文 is unmodified."""

    @classmethod
    def yuewen_unmodified_error(cls, idx: int) -> str:
        """Error message when revised 粤文 is unmodified.

        Arguments:
            idx: index of subtitle
        Returns:
            error message when revised 粤文 is unmodified
        """
        return cls.yuewen_unmodified_error_template.format(idx=idx)

    yuewen_revised_provided_note_missing_error_template: ClassVar[str] = (
        "Answer's 粤文 text {idx} is modified relative to query's 粤文 text {idx}, but "
        "no note is provided, if revision is needed a note must be provided."
    )
    """Error template when revised 粤文 is provided but note is missing."""

    @classmethod
    def yuewen_revised_provided_note_missing_error(cls, idx: int) -> str:
        """Error message when revised 粤文 is provided but note is missing.

        Arguments:
            idx: index of subtitle
        Returns:
            error message when revised 粤文 is provided but note is missing
        """
        return cls.yuewen_revised_provided_note_missing_error_template.format(idx=idx)

    yuewen_revised_missing_note_provided_error_template: ClassVar[str] = (
        "Answer's 粤文 text {idx} is not modified relative to query's 粤文 text {idx}, "
        "but a note is provided, if no revisions are needed an empty string must be "
        "provided."
    )
    """Error template when revised 粤文 is missing but note is provided."""

    @classmethod
    def yuewen_revised_missing_note_provided_error(cls, idx: int) -> str:
        """Error message when revised 粤文 is missing but note is provided.

        Arguments:
            idx: index of subtitle
        Returns:
            error message when revised 粤文 is missing but note is provided
        """
        return cls.yuewen_revised_missing_note_provided_error_template.format(idx=idx)
