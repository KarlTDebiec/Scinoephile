#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 proofing test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field

from .answer import ProofingAnswer
from .prompt import ProofingPrompt
from .query import ProofingQuery

__all__ = ["ProofingTestCase"]


class ProofingTestCase(
    ProofingQuery, ProofingAnswer, TestCase[ProofingQuery, ProofingAnswer], ABC
):
    """Abstract base class for 粤文 proofing test cases."""

    answer_cls: ClassVar[type[ProofingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ProofingQuery]]
    """Query class for this test case."""
    text: ClassVar[type[ProofingPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [
            f"{ProofingTestCase.__name__}.get_test_case_cls({self.text.__name__})("
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
        if self.yuewen != self.yuewen_proofread:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.yuewen != self.yuewen_proofread and not self.note:
            raise ValueError(self.text.yuewen_modified_note_missing_error)
        if self.yuewen == self.yuewen_proofread and self.note:
            raise ValueError(self.text.yuewen_unmodified_note_provided_error)
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls, text: type[ProofingPrompt] = ProofingPrompt
    ) -> type[Self]:
        """Get concrete test case class with provided text.

        Arguments:
            text: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        query_cls = ProofingQuery.get_query_cls(text)
        answer_cls = ProofingAnswer.get_answer_cls(text)
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[ProofingQuery]], query_cls),
            answer_cls=(ClassVar[type[ProofingAnswer]], answer_cls),
            text=(ClassVar[type[ProofingPrompt]], text),
        )
