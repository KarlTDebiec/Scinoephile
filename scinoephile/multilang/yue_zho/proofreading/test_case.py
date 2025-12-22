#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for 粤文 vs. 中文 proofreading test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model

from scinoephile.llms.base.models import get_model_name
from scinoephile.llms.dual_single import DualSingleQuery, DualSingleTestCase

from .answer import YueZhoProofreadingAnswer
from .prompts import YueZhoHansProofreadingPrompt

__all__ = ["YueZhoProofreadingTestCase"]


class YueZhoProofreadingTestCase(DualSingleTestCase, ABC):
    """ABC for 粤文 vs. 中文 proofreading test cases."""

    answer_cls: ClassVar[type[YueZhoProofreadingAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[DualSingleQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[YueZhoHansProofreadingPrompt]]
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
        min_difficulty = super(DualSingleTestCase, self).get_min_difficulty()
        if self.answer is None:
            return min_difficulty

        yuewen = getattr(self.query, self.prompt_cls.src_1, None)
        yuewen_proofread = getattr(self.answer, self.prompt_cls.output, None)
        if yuewen != yuewen_proofread:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[YueZhoHansProofreadingPrompt],
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = DualSingleQuery.get_query_cls(prompt_cls)
        answer_cls = YueZhoProofreadingAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
