#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for 粤文 proofing test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.llms.base import TestCase
from scinoephile.llms.base.models import get_model_name

from .answer import ProofingAnswer
from .prompt import ProofingPrompt
from .query import ProofingQuery

__all__ = ["ProofingTestCase"]


class ProofingTestCase(TestCase, ABC):
    """ABC for 粤文 proofing test cases."""

    answer_cls: ClassVar[type[ProofingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ProofingQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ProofingPrompt]]
    """Text for LLM correspondence."""

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
        if self.answer is None:
            return min_difficulty

        yuewen = getattr(self.query, self.prompt_cls.yuewen_field, None)
        yuewen_proofread = getattr(
            self.answer, self.prompt_cls.yuewen_proofread_field, None
        )
        if yuewen != yuewen_proofread:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        yuewen = getattr(self.query, self.prompt_cls.yuewen_field, None)
        yuewen_proofread = getattr(
            self.answer, self.prompt_cls.yuewen_proofread_field, None
        )
        note = getattr(self.answer, self.prompt_cls.note_field, None)
        if yuewen != yuewen_proofread and not note:
            raise ValueError(self.prompt_cls.yuewen_modified_note_missing_error)
        if yuewen == yuewen_proofread and note:
            raise ValueError(self.prompt_cls.yuewen_unmodified_note_provided_error)
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[ProofingPrompt] = ProofingPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = ProofingQuery.get_query_cls(prompt_cls)
        answer_cls = ProofingAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
