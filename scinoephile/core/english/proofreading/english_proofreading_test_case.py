#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English proofreading test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar

from pydantic import create_model, model_validator

from scinoephile.core.abcs import TestCase
from scinoephile.core.english.proofreading.english_proofreading_answer import (
    EnglishProofreadingAnswer,
)
from scinoephile.core.english.proofreading.english_proofreading_llm_text import (
    EnglishProofreadingLLMText,
)
from scinoephile.core.english.proofreading.english_proofreading_query import (
    EnglishProofreadingQuery,
)
from scinoephile.core.models import format_field


class EnglishProofreadingTestCase(
    TestCase[EnglishProofreadingQuery, EnglishProofreadingAnswer], ABC
):
    """Abstract base class for English proofreading test cases."""

    answer_cls: ClassVar[type[EnglishProofreadingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[EnglishProofreadingQuery]]
    """Query class for this test case."""
    text: ClassVar[type[EnglishProofreadingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def noop(self) -> bool:
        """Whether this test case is a no-op."""
        for idx in range(1, self.size + 1):
            revised = getattr(self, f"revised_{idx}")
            if revised != "":
                return False
        return True

    @property
    def size(self) -> int:
        """Size of the test case."""
        idxs = [
            int(s.split("_")[1]) - 1
            for s in self.query_fields
            if s.startswith("subtitle_")
        ]
        return max(idxs) + 1

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [
            f"{EnglishProofreadingTestCase.__name__}.get_test_case_cls({self.size}, "
            f"{self.text.__name__})("
        ]
        for field in self.query_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        for field in self.answer_fields:
            value = getattr(self, field)
            if value == "":
                continue
            lines.append(format_field(field, value))
        for field in self.test_case_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        lines.append(")")
        return "\n".join(lines)

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the test case properties.

        0: No change needed
        1: Change needed
        2: Difficult change needed, worthy of inclusion in prompt or difficult test set
        3: Not considered realistic for LLM to handle correctly

        Returns:
            minimum difficulty level based on the test case properties
        """
        min_difficulty = super().get_min_difficulty()
        if not self.noop:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> EnglishProofreadingTestCase:
        """Ensure query and answer are consistent with one another."""
        for idx in range(self.size):
            subtitle = getattr(self, f"subtitle_{idx + 1}")
            revised = getattr(self, f"revised_{idx + 1}")
            note = getattr(self, f"note_{idx + 1}")
            if revised != "":
                if subtitle == revised:
                    raise ValueError(
                        self.text.subtitle_revised_equal_error.format(idx + 1)
                    )
                if note == "":
                    raise ValueError(self.text.note_missing_error.format(idx + 1))
            elif note != "":
                raise ValueError(self.text.revised_missing_error.format(idx + 1))
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        text: type[EnglishProofreadingLLMText] = EnglishProofreadingLLMText,
    ) -> type[EnglishProofreadingTestCase]:
        """Get test case class for English proofing.

        Arguments:
            size: number of subtitles
            text: LLMText providing descriptions and messages
        Returns:
            EnglishProofreadingTestCase type with appropriate fields and descriptions
        Raises:
            ScinoephileError: if missing indices are out of range
        """
        query_cls = EnglishProofreadingQuery.get_query_cls(size, text)
        answer_cls = EnglishProofreadingAnswer.get_answer_cls(size, text)
        model = create_model(
            f"{cls.__name__}_{size}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[EnglishProofreadingQuery]], query_cls),
            answer_cls=(ClassVar[type[EnglishProofreadingAnswer]], answer_cls),
            text=(ClassVar[type[EnglishProofreadingLLMText]], text),
        )

        return model
