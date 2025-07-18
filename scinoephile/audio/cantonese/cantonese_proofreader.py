#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 粤文 subtitles based on 中文."""

from __future__ import annotations

from typing import override

from scinoephile.audio.models import ProofreadAnswer, ProofreadQuery
from scinoephile.audio.testing import ProofreadTestCase
from scinoephile.core.abcs import LLMQueryer


class CantoneseProofreader(
    LLMQueryer[ProofreadQuery, ProofreadAnswer, ProofreadTestCase]
):
    """Proofreads a 粤文 subtitle based on the corresponding 中文."""

    @property
    @override
    def answer_cls(self) -> type[ProofreadAnswer]:
        """Answer class."""
        return ProofreadAnswer

    @property
    @override
    def answer_example(self) -> ProofreadAnswer:
        """Example answer."""
        return ProofreadAnswer(
            yuewen_proofread="我哋要盡快走",
            note="Replaced '我地' with '我哋' to follow standard written Cantonese.",
        )

    @property
    @override
    def answer_template(self) -> str:
        """Answer template."""
        return "粤文 proofread:\n{yuewen_proofread}\nNote:\n{note}\n"

    @property
    @override
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that proofreads 粤文 transcription of spoken
        Cantonese based on the corresponding 中文 text.
        Your goal is to correct only clear transcription errors in the 粤文 —
        specifically, cases where the transcriber likely misheard a word and wrote a
        similar-sounding but incorrect one.
        Do not rewrite correct phrases to match the 中文 wording.
        Do not adjust phrasing, grammar, or classifiers unless there's a clear
        transcription mistake.
        Only correct 粤文 if there's a plausible phonetic confusion (e.g., 临盘 vs.
        临盆).

        Remember:
        - The 粤文 transcription does not need to match the 中文 word-for-word.
        - The speaker may naturally use different wording in Cantonese.
        - Many differences in meaning, tone, or grammar are acceptable if they are not
          transcription errors.

        Include a one-sentence explanation in English for any correction you make.
        If you make no changes, return an empty string for the note.

        Your response must be a JSON object with the following structure:
        """

    @property
    @override
    def query_cls(self) -> type[ProofreadQuery]:
        """Query class."""
        return ProofreadQuery

    @property
    @override
    def query_template(self) -> str:
        """Query template."""
        return "中文:\n{zhongwen}\n粤文 to proofread:\n{yuewen}\n"

    @property
    @override
    def test_case_cls(self) -> type[ProofreadTestCase]:
        """Test case class."""
        return ProofreadTestCase
