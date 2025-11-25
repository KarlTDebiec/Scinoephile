#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread English subtitles."""

from __future__ import annotations

from scinoephile.core.abcs import DynamicLLMQueryer
from scinoephile.core.english.proofreading.english_proofreading_answer import (
    EnglishProofreadingAnswer,
)
from scinoephile.core.english.proofreading.english_proofreading_query import (
    EnglishProofreadingQuery,
)
from scinoephile.core.english.proofreading.english_proofreading_test_case import (
    EnglishProofreadingTestCase,
)


class EnglishProofreadingLLMQueryer[
    TQuery: EnglishProofreadingQuery,
    TAnswer: EnglishProofreadingAnswer,
    TTestCase: EnglishProofreadingTestCase,
](
    DynamicLLMQueryer[
        EnglishProofreadingQuery, EnglishProofreadingAnswer, EnglishProofreadingTestCase
    ]
):
    """Queries LLM to proofread English subtitles."""

    @property
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

    @property
    def encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for test_case in self._encountered_test_cases.values():
            source_str: str = test_case.source_str
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "]"
        return test_case_log_str

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
