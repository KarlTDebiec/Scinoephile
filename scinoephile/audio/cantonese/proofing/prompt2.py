#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 transcription proofing."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.english.abcs.prompt2 import EnglishPrompt2
from scinoephile.core.text import get_dedented_and_compacted_multiline_text

__all__ = ["ProofingPrompt2"]


class ProofingPrompt2(EnglishPrompt2):
    """Text for LLM correspondence for 粤文 transcription proofing."""

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

    # Query descriptions
    zhongwen_description: ClassVar[str] = "Known 中文 of subtitle"
    """Description of 'zhongwen' field."""

    yuewen_description: ClassVar[str] = "Transcribed 粤文 of subtitle to proofread"
    """Description of 'yuewen' field."""

    # Query validation errors
    zhongwen_missing_error: ClassVar[str] = "Query must have 中文 subtitle."
    """Error message when 'zhongwen' is missing."""

    yuewen_missing_error: ClassVar[str] = "Query must have 粤文 subtitle to proofread."
    """Error message when 'yuewen' is missing."""

    # Answer descriptions
    yuewen_proofread_description: ClassVar[str] = "Proofread 粤文 of subtitle"
    """Description of 'yuewen_proofread' field."""

    note_description: ClassVar[str] = "Description of corrections made"
    """Description of 'note' field."""

    # Answer validation errors
    yuewen_proofread_and_note_missing_error: ClassVar[str] = (
        "If Answer omits proofread 粤文 of subtitle to indicate that 粤文 is "
        "believed to be a complete mistranscription of the spoken Cantonese "
        "and should be omitted, it must also include a note describing the issue."
    )
    """Error message when both 'yuewen_proofread' and 'note' are missing."""

    # Test case validation errors
    yuewen_modified_note_missing_error: ClassVar[str] = (
        "Answer's proofread 粤文 of subtitle is modified relative to query's "
        "粤文 of subtitle, but no note is provided."
    )
    """Error message when proofread 粤文 is modified but note is omitted."""

    yuewen_unmodified_note_provided_error: ClassVar[str] = (
        "Answer's proofread 粤文 of subtitle is identical to query's 粤文 of "
        "subtitle, but a note is provided."
    )
