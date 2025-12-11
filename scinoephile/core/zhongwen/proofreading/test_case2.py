#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Zhongwen proofreading test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import TestCase2
from scinoephile.core.models import get_cls_name

from .answer2 import ZhongwenProofreadingAnswer2
from .prompt2 import ZhongwenProofreadingPrompt2
from .query2 import ZhongwenProofreadingQuery2

__all__ = ["ZhongwenProofreadingTestCase2"]


class ZhongwenProofreadingTestCase2(
    TestCase2[ZhongwenProofreadingQuery2, ZhongwenProofreadingAnswer2],
    ABC,
):
    """Abstract base class for Zhongwen proofreading test cases."""

    answer_cls: ClassVar[type[ZhongwenProofreadingAnswer2]]  # type: ignore
    """Answer class for this test case."""
    query_cls: ClassVar[type[ZhongwenProofreadingQuery2]]  # type: ignore
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ZhongwenProofreadingPrompt2]]  # type: ignore
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

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
        if self.answer is not None:
            if any(
                getattr(self.answer, f"xiugai_{idx}") != ""
                for idx in range(1, self.size + 1)
            ):
                min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        subtitle_revised_equal_error = self.prompt_cls.subtitle_revised_equal_error
        note_missing_error = self.prompt_cls.note_missing_error
        revised_missing_error = self.prompt_cls.revised_missing_error

        for idx in range(self.size):
            subtitle = getattr(self.query, f"zimu_{idx + 1}")
            revised = getattr(self.answer, f"xiugai_{idx + 1}")
            note = getattr(self.answer, f"beizhu_{idx + 1}")
            if revised != "":
                if subtitle == revised:
                    raise ValueError(subtitle_revised_equal_error.format(idx=idx + 1))
                if note == "":
                    raise ValueError(note_missing_error.format(idx=idx + 1))
            elif note != "":
                raise ValueError(revised_missing_error.format(idx=idx + 1))
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[ZhongwenProofreadingPrompt2] = ZhongwenProofreadingPrompt2,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_cls_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        query_cls = ZhongwenProofreadingQuery2.get_query_cls(size, prompt_cls)
        answer_cls = ZhongwenProofreadingAnswer2.get_answer_cls(size, prompt_cls)
        fields = {
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
        model.size = size
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data dictionary
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case class
        """
        size = sum(1 for key in data["query"] if key.startswith("zimu_"))
        test_case_cls = cls.get_test_case_cls(size=size, **kwargs)
        return test_case_cls
