#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 粤文 subtitles based on 中文."""

from __future__ import annotations

from functools import cached_property
from typing import override

from scinoephile.audio.cantonese.proofing.proof_answer import ProofAnswer
from scinoephile.audio.cantonese.proofing.proof_query import ProofQuery
from scinoephile.audio.cantonese.proofing.proof_test_case import ProofTestCase
from scinoephile.core.abcs import FixedLLMQueryer


class Proofer(FixedLLMQueryer[ProofQuery, ProofAnswer, ProofTestCase]):
    """Proofreads 粤文 text based on the corresponding 中文."""

    @cached_property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for proofreading 粤文 (yuewen) subtitles of Cantonese speech.
        For reference, you are provided the corresponding 中文 (zhongwen) subtitles of
        the same Cantonese speech.
        Your goal is to correct only clear transcription errors in the yuewen —
        specifically, cases where the transcriber likely misheard a word and wrote a
        similar-sounding but incorrect one.
        Do not rewrite correct phrases to match the zhongwen wording.
        Do not adjust phrasing, grammar, or classifiers unless there's a clear
        transcription mistake.
        Only correct yuewen if there's a plausible phonetic confusion.
        If there is truly zero correspondence between the yuewen and zhongwen,
        indicating a complete mistranscription of the spoken Cantonese, return an empty
        string for yuewen.
        If you make changes, include a one-sentence note in English explaining them.
        Include the Yale romanization of Cantonese for any character substitutions.
        If you make no changes, return an empty string for the note.

        Remember:
        - The yuewen transcription does not need to match the zhongwen word-for-word.
        - The speaker may naturally use different wording in the spoken Cantonese than
          present in the zhongwen.
        - Many differences in meaning, tone, or grammar are acceptable if they are not
          transcription errors.
        """
