#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 proofing test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.audio.cantonese.proofing.proofing_answer import ProofingAnswer
from scinoephile.audio.cantonese.proofing.proofing_llm_text import ProofingLLMText
from scinoephile.audio.cantonese.proofing.proofing_query import ProofingQuery
from scinoephile.core.abcs import TestCase


class ProofingTestCase(
    ProofingQuery, ProofingAnswer, TestCase[ProofingQuery, ProofingAnswer], ABC
):
    """Abstract base class for 粤文 proofing test cases."""

    answer_cls: ClassVar[type[ProofingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ProofingQuery]]
    """Query class for this test case."""
    text: ClassVar[type[ProofingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def noop(self) -> bool:
        """Return whether this test case is a no-op."""
        return self.yuewen == self.yuewen_proofread

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
        cls, text: type[ProofingLLMText] = ProofingLLMText
    ) -> type[Self]:
        """Get concrete test case class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        query_cls = ProofingQuery.get_query_cls(text)
        answer_cls = ProofingAnswer.get_answer_cls(text)
        model = create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[ProofingQuery]], query_cls),
            answer_cls=(ClassVar[type[ProofingAnswer]], answer_cls),
            text=(ClassVar[type[ProofingLLMText]], text),
        )

        return model
