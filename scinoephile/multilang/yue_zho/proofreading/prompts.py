#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 粤文 proofreading against 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.eng.prompts import EngPrompt
from scinoephile.llms.dual_single import DualSinglePrompt

__all__ = ["YueZhoProofreadingPrompt"]


class YueZhoProofreadingPrompt(DualSinglePrompt, EngPrompt):
    """LLM correspondence text for 粤文 proofreading against 中文."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        You are responsible for proofreading 粤文 subtitles of Cantonese speech.
        For reference, you are provided the corresponding 中文 subtitles of the same
        Cantonese speech.
        Your goal is to correct only clear transcription errors in the 粤文 —
        specifically, cases where the transcriber likely misheard a word and wrote a
        similar-sounding but incorrect one.
        Do not rewrite correct phrases to match the 中文 wording.
        Do not adjust phrasing, grammar, or classifiers unless there's a clear
        transcription mistake.
        Only correct 粤文 if there's a plausible phonetic confusion (e.g., 临盘 vs.
        临盆).
        If there is truly zero correspondence between the 粤文 and 中文, indicating a
        complete mistranscription of the spoken Cantonese, return empty string for the
        粤文 and a note explaining the lack of correspondence.

        Remember:
        - The 粤文 transcription does not need to match the 中文 word-for-word.
        - The speaker may naturally use different wording in Cantonese.
        - Many differences in meaning, tone, or grammar are acceptable if they are not
          transcription errors.

        Include a one-sentence explanation in English for any correction you make.
        If you make no changes, return an empty string for the note.""")
    """Base system prompt."""

    # Query fields
    source_one_field: ClassVar[str] = "yuewen"
    """Name of source one field in query."""

    source_one_description: ClassVar[str] = "Transcribed 粤文 of subtitle to proofread"
    """Description of source one field in query."""

    source_two_field: ClassVar[str] = "zhongwen"
    """Name for source two field in query."""

    source_two_description: ClassVar[str] = "Known 中文 of subtitle"
    """Description of source two field in query."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = (
        "Query must have 粤文 subtitle to proofread."
    )
    """Error when source one field is missing from query."""

    source_two_missing_error: ClassVar[str] = "Query must have 中文 subtitle."
    """Error when source two field is missing from query."""

    sources_equal_error: ClassVar[str] = "Subtitle text from two sources must differ."
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output_field: ClassVar[str] = "yuewen_proofread"
    """Name of output field in answer."""

    output_description: ClassVar[str] = (
        "Proofread 粤文 of subtitle (may be empty if the 粤文 should be omitted)"
    )
    """Description of output field in answer."""

    note_field: ClassVar[str] = "note"
    """Name of note field in answer."""

    note_description: ClassVar[str] = "Description of corrections made"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_error: ClassVar[str] = (
        "Answer must include proofread 粤文 of subtitle (use empty string if omitting)."
    )
    """Error when output field is missing from answer."""

    note_missing_error: ClassVar[str] = (
        "Answer must include a note describing the changes (empty if none)."
    )
    """Error when note field is missing from answer."""
