#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription review."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english.abcs import EnglishLLMText
from scinoephile.core.text import get_dedented_and_compacted_multiline_text


class ReviewLLMText(EnglishLLMText):
    """Text for LLM correspondence for 粤文 transcription review."""

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

    # Query descriptions
    zhongwen_description: ClassVar[str] = "Known 中文 of subtitle {idx}"
    """Description of 'zhongwen_{idx}' field."""

    yuewen_description: ClassVar[str] = "Transcribed 粤文 of subtitle {idx}"
    """Description of 'yuewen_{idx}' field."""

    # Answer descriptions
    yuewen_revised_description: ClassVar[str] = "Revised 粤文 of subtitle {idx}"
    """Description of 'yuewen_revised_{idx}' field."""

    note_description: ClassVar[str] = "Note concerning revision of subtitle {idx}"
    """Description of 'note_{idx}' field."""

    # Test case validation errors
    yuewen_unmodified_error: ClassVar[str] = (
        "Answer's revised 粤文 text {idx} is not modified relative to query's 粤文 "
        "text {idx}, if no revision is needed an empty string must be provided."
    )
    """Error message when revised 粤文 is unmodified."""

    yuewen_revised_provided_note_missing_error: ClassVar[str] = (
        "Answer's 粤文 text {idx} is modified relative to query's 粤文 text {idx}, but "
        "no note is provided, if revision is needed a note must be provided."
    )
    """Error message when revised 粤文 is provided but note is missing."""

    yuewen_revised_missing_note_provided_error: ClassVar[str] = (
        "Answer's 粤文 text {idx} is not modified relative to query's 粤文 text {idx}, "
        "but a note is provided, if no revisions are needed an empty string must be "
        "provided."
    )
