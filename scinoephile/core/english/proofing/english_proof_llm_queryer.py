#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreads English subtitles."""

from __future__ import annotations

from functools import cached_property

from scinoephile.core.abcs import DynamicLLMQueryer
from scinoephile.core.english.proofing.abcs import (
    EnglishProofAnswer,
    EnglishProofQuery,
    EnglishProofTestCase,
)


class EnglishProofLLMQueryer[
    TQuery: EnglishProofQuery,
    TAnswer: EnglishProofAnswer,
    TTestCase: EnglishProofTestCase,
](DynamicLLMQueryer[EnglishProofQuery, EnglishProofAnswer, EnglishProofTestCase]):
    """Proofreads English subtitles."""

    @cached_property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return """
        You are responsible for proofreading English subtitles generated using OCR.
        For each subtitle, you are to provide revised subtitle only if revisions are
        necessary.
        If revisions are needed, return the full revised subtitle, and a note describing
        the changes made.
        If no revisions are needed, return an empty string for the revised subtitle and
        its note.
        Make changes only when necessary to correct errors clearly resulting from OCR.
        Do not add stylistic changes or improve phrasing.
        Do not change colloquialisms or dialect such as 'gonna' or 'wanna'.
        Do not change spelling from British to American English or vice versa.
        Do not remove subtitle markup such as italics ('{\\i1}' and '{\\i0}').
        Do not remove newlines ('\\n').
        """

    @staticmethod
    def get_answer_example(answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer."""
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "revised_":
                answer_values[key] = (
                    f"Subtitle {idx} revised, or an empty string if no revision is "
                    f"necessary."
                )
            else:
                answer_values[key] = (
                    f"Note concerning revisions to subtitle {idx}, or an empty string "
                    f"if no revision is necessary."
                )
        return answer_cls(**answer_values)
