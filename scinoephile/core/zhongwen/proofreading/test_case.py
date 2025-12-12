#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.llms import TestCase
from scinoephile.core.models import get_model_name

from .answer import ZhongwenProofreadingAnswer
from .prompt import ZhongwenProofreadingPrompt
from .query import ZhongwenProofreadingQuery

__all__ = ["ZhongwenProofreadingTestCase"]


class ZhongwenProofreadingTestCase(TestCase, ABC):
    """Abstract base class for 中文 proofreading test cases."""

    answer_cls: ClassVar[type[ZhongwenProofreadingAnswer]]  # type: ignore
    """Answer class for this test case."""
    query_cls: ClassVar[type[ZhongwenProofreadingQuery]]  # type: ignore
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ZhongwenProofreadingPrompt]]  # type: ignore
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
        prompt_cls: type[ZhongwenProofreadingPrompt] = ZhongwenProofreadingPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        query_cls = ZhongwenProofreadingQuery.get_query_cls(size, prompt_cls)
        answer_cls = ZhongwenProofreadingAnswer.get_answer_cls(size, prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        model.size = size
        return model

    @classmethod
    def get_test_case_cls_from_data(
        cls, data: dict, prompt_cls: type[ZhongwenProofreadingPrompt], **kwargs: Any
    ) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data dictionary
            prompt_cls: Prompt providing descriptions and messages
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            TestCase type with appropriate configuration
        """
        size = sum(1 for key in data["query"] if key.startswith("zimu_"))
        return cls.get_test_case_cls(size=size, prompt_cls=prompt_cls, **kwargs)
