#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 proofing test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import TestCase2
from scinoephile.core.models import get_model_name

from .answer2 import ProofingAnswer2
from .prompt2 import ProofingPrompt2
from .query2 import ProofingQuery2

__all__ = ["ProofingTestCase2"]


class ProofingTestCase2(TestCase2, ABC):
    """Abstract base class for 粤文 proofing test cases."""

    answer_cls: ClassVar[type[ProofingAnswer2]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ProofingQuery2]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ProofingPrompt2]]
    """Text strings to be used for corresponding with LLM."""

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

        yuewen = getattr(self.query, "yuewen", None)
        yuewen_proofread = getattr(self.answer, "yuewen_proofread", None)
        if yuewen != yuewen_proofread:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        yuewen = getattr(self.query, "yuewen", None)
        yuewen_proofread = getattr(self.answer, "yuewen_proofread", None)
        note = getattr(self.answer, "note", None)
        if yuewen != yuewen_proofread and not note:
            raise ValueError(self.prompt_cls.yuewen_modified_note_missing_error)
        if yuewen == yuewen_proofread and note:
            raise ValueError(self.prompt_cls.yuewen_unmodified_note_provided_error)
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[ProofingPrompt2] = ProofingPrompt2,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = ProofingQuery2.get_query_cls(prompt_cls)
        answer_cls = ProofingAnswer2.get_answer_cls(prompt_cls)
        fields: dict[str, Any] = {
            "query": (query_cls, Field(...)),
            "answer": (answer_cls | None, Field(default=None)),
            "difficulty": (
                int,
                Field(0, description=prompt_cls.difficulty_description),
            ),
            "prompt": (
                bool,
                Field(False, description=prompt_cls.prompt_description),
            ),
            "verified": (
                bool,
                Field(False, description=prompt_cls.verified_description),
            ),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
