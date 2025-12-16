#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 粤文."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text

__all__ = [
    "YuePrompt",
]


class YuePrompt(Prompt, ABC):
    """LLM correspondence text for 粤文."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        You are responsible for performing final review of 粤文 subtitles of Cantonese
        speech.
        Each 粤文 subtitle has already been proofed individually against its paired
        中文 subtitle, and any discrepancies apparent within that pairing have been
        resolved.
        Your focus is on resolving issues in the 粤文 subtitle that may not have been
        apparent within its individual pairing, but which may be apparent when the
        entire series of subtitles is considered together.
        You are not reviewing for quality of writing, grammar, or style, only for
        correctness of the 粤文 transcription.
        Keeping in mind that the 粤文 subtitle is a transcription of spoken Cantonese,
        and the 中文 subtitle is not expected to match word-for-word.
        For each 粤文 subtitle, you are to provide revised 粤文 subtitle only if
        revisions are necessary.
        If no revisions are are necessary to a particular 粤文 subtitle, return an
        empty string for that subtitle.
        If revisions are needed, return the full revised 粤文 subtitle, and include a
        note describing in English the changes made.
        If no revisions are needed return an empty string for the note.""")
    """Base system prompt."""

    # Query fields
    zhongwen_prefix: ClassVar[str] = "zhongwen_"
    """Prefix of 中文 field in query."""

    @classmethod
    def zhongwen_field(cls, idx: int) -> str:
        """Name of 中文 field in query.

        Arguments:
            idx: index of subtitle
        Returns:
            name of 中文 field in query
        """
        return f"{cls.zhongwen_prefix}{idx}"

    zhongwen_description_template: ClassVar[str] = "Known 中文 of subtitle {idx}"
    """Description template for 中文 field in query."""

    @classmethod
    def zhongwen_description(cls, idx: int) -> str:
        """Description of 中文 field in query.

        Arguments:
            idx: index of subtitle
        Returns:
            description of 中文 field in query
        """
        return cls.zhongwen_description_template.format(idx=idx)

    yuewen_prefix: ClassVar[str] = "yuewen_"
    """Prefix of 粤文 field in query."""

    @classmethod
    def yuewen_field(cls, idx: int) -> str:
        """Name of 粤文 field in query.

        Arguments:
            idx: index of subtitle
        Returns:
            name of 粤文 field in query
        """
        return f"{cls.yuewen_prefix}{idx}"

    yuewen_description_template: ClassVar[str] = "Transcribed 粤文 of subtitle {idx}"
    """Description template for 粤文 field in query."""

    @classmethod
    def yuewen_description(cls, idx: int) -> str:
        """Description of 粤文 field in query.

        Arguments:
            idx: index of subtitle
        Returns:
            description of 粤文 field in query
        """
        return cls.yuewen_description_template.format(idx=idx)

    # Answer fields
    yuewen_revised_prefix: ClassVar[str] = "yuewen_revised_"
    """Prefix of revised 粤文 field in answer."""

    @classmethod
    def yuewen_revised_field(cls, idx: int) -> str:
        """Name of revised 粤文 field in answer.

        Arguments:
            idx: index of subtitle
        Returns:
            name of revised 粤文 field in answer
        """
        return f"{cls.yuewen_revised_prefix}{idx}"

    yuewen_revised_description_template: ClassVar[str] = (
        "Revised 粤文 of subtitle {idx}"
    )
    """Description template for revised 粤文 field in answer."""

    @classmethod
    def yuewen_revised_description(cls, idx: int) -> str:
        """Description of revised 粤文 field in answer.

        Arguments:
            idx: index of subtitle
        Returns:
            description of revised 粤文 field in answer
        """
        return cls.yuewen_revised_description_template.format(idx=idx)

    note_prefix: ClassVar[str] = "note_"
    """Prefix of note field in answer."""

    @classmethod
    def note_field(cls, idx: int) -> str:
        """Name of note field in answer.

        Arguments:
            idx: index of subtitle
        Returns:
            name of note field in answer
        """
        return f"{cls.note_prefix}{idx}"

    note_description_template: ClassVar[str] = (
        "Note concerning revision of subtitle {idx}"
    )
    """Description template for note field in answer."""

    @classmethod
    def note_description(cls, idx: int) -> str:
        """Description of note field in answer.

        Arguments:
            idx: index of subtitle
        Returns:
            description of note field in answer
        """
        return cls.note_description_template.format(idx=idx)

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
