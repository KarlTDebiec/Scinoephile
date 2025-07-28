#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 粤文 subtitles based on 中文."""

from __future__ import annotations

from functools import cached_property
from typing import override

from scinoephile.audio.cantonese.proofing.proof_answer import ProofAnswer
from scinoephile.audio.cantonese.proofing.proof_query import ProofQuery
from scinoephile.audio.cantonese.proofing.proof_test_case import ProofTestCase
from scinoephile.core.abcs import LLMQueryer


class Proofer(LLMQueryer[ProofQuery, ProofAnswer, ProofTestCase]):
    """Proofreads 粤文 text based on the corresponding 中文."""

    @cached_property
    @override
    def answer_example(self) -> ProofAnswer:
        """Example answer."""
        return ProofAnswer(
            yuewen_proofread="我哋要盡快走",
            note="Replaced '我地' with '我哋' to follow standard written Cantonese.",
        )

    @cached_property
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
        If there is truly zero correspondence between the 粤文 and 中文, indicating a
        complete transcription failure, return empty string for the 粤文 and a note 
        explaining the lack of correspondence.

        Remember:
        - The 粤文 transcription does not need to match the 中文 word-for-word.
        - The speaker may naturally use different wording in Cantonese.
        - Many differences in meaning, tone, or grammar are acceptable if they are not
          transcription errors.

        Include a one-sentence explanation in English for any correction you make.
        If you make no changes, return an empty string for the note.
        """

    @property
    def test_case_log_str(self) -> str:
        """String representation of all test cases in the log.

        If the test case asks for changes, difficulty is 1.
        If the test case is included in the prompt, difficulty is 2.
        """
        test_case_log_str = "[\n"

        for key, value in self._test_case_log.items():
            source_str: str = value.source_str[:-1]

            difficulty = value.difficulty
            if value.yuewen != value.yuewen_proofread:
                difficulty = 1
            if key in self._examples_log:
                difficulty = 2
                source_str += "    include_in_prompt=True,\n"
            if difficulty:
                source_str += f"    difficulty={difficulty},\n"
            source_str += ")"
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "\n]"
        return test_case_log_str
