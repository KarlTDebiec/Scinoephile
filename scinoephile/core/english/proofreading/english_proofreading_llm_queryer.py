#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Queries LLM to proofread English subtitles."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.abcs import DynamicLLMQueryer
from scinoephile.core.english.proofreading.english_proofreading_answer import (
    EnglishProofreadingAnswer,
)
from scinoephile.core.english.proofreading.english_proofreading_llm_text import (
    EnglishProofreadingLLMText,
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

    text: ClassVar[type[EnglishProofreadingLLMText]] = EnglishProofreadingLLMText

    @property
    def encountered_test_cases_source_str(self) -> str:
        """String representation of all test cases in the log."""
        test_case_log_str = "[\n"
        for test_case in self._encountered_test_cases.values():
            source_str: str = test_case.source_str
            test_case_log_str += f"{source_str},\n"
        test_case_log_str += "]"
        return test_case_log_str

    def get_answer_example(self, answer_cls: type[TAnswer]) -> TAnswer:
        """Example answer.

        Arguments:
            answer_cls: Answer class
        Returns:
            Example answer
        """
        answer_values = {}
        for key in answer_cls.model_fields.keys():
            kind, idx = key.rsplit("_", 1)
            if kind == "revised_":
                answer_values[key] = (
                    self.text.answer_example_revised_description.format(idx=idx)
                )
            else:
                answer_values[key] = self.text.answer_example_note_description.format(
                    idx=idx
                )

        return answer_cls(**answer_values)
