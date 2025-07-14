# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads 粤文 subtitles based on 中文."""

from __future__ import annotations

from scinoephile.audio.models import ProofreadAnswer, ProofreadQuery
from scinoephile.audio.testing import ProofreadTestCase
from scinoephile.core.abcs import LLMQueryer


class CantoneseProofreader(
    LLMQueryer[ProofreadQuery, ProofreadAnswer, ProofreadTestCase]
):
    """Proofreads a 粤文 subtitle based on the corresponding 中文."""

    @property
    def answer_cls(self) -> type[ProofreadAnswer]:
        """Answer class."""
        return ProofreadAnswer

    @property
    def answer_example(self) -> ProofreadAnswer:
        """Example answer."""
        return ProofreadAnswer(yuewen_proofread="粤文校对", note="")

    @property
    def answer_template(self) -> str:
        """Answer template."""
        return "粤文 proofread:\n{yuewen_proofread}\nNote:\n{note}\n"

    @property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are a helpful assistant that proofreads a single-line 粤文 subtitle of
        spoken Cantonese based on the corresponding single-line 中文 subtitle.
        Correct any mistakes in the 粤文 transcription while keeping the meaning
        consistent with the spoken Cantonese.
        If you do not make any changes, return an empty string for the note.
        Your response must be a JSON object with the following structure:
        """

    @property
    def query_cls(self) -> type[ProofreadQuery]:
        """Query class."""
        return ProofreadQuery

    @property
    def query_template(self) -> str:
        """Query template."""
        return "中文:\n{zhongwen}\n粤文 original:\n{yuewen}\n"

    @property
    def test_case_cls(self) -> type[ProofreadTestCase]:
        """Test case class."""
        return ProofreadTestCase
