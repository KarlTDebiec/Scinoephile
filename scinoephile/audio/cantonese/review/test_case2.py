#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription review test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import TestCase2
from scinoephile.core.models import get_model_name

from .answer2 import ReviewAnswer2
from .prompt2 import ReviewPrompt2
from .query2 import ReviewQuery2

__all__ = ["ReviewTestCase2"]


class ReviewTestCase2(TestCase2[ReviewQuery2, ReviewAnswer2], ABC):
    """Abstract base class for 粤文 transcription review test cases."""

    answer_cls: ClassVar[type[ReviewAnswer2]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ReviewQuery2]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ReviewPrompt2]]
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        yuewen_unmodified_error = self.prompt_cls.yuewen_unmodified_error
        yuewen_revised_provided_note_missing_error = (
            self.prompt_cls.yuewen_revised_provided_note_missing_error
        )
        yuewen_revised_missing_note_provided_error = (
            self.prompt_cls.yuewen_revised_missing_note_provided_error
        )

        for idx in range(self.size):
            yuewen = getattr(self.query, f"yuewen_{idx + 1}")
            yuewen_revised = getattr(self.answer, f"yuewen_revised_{idx + 1}")
            note = getattr(self.answer, f"note_{idx + 1}")
            if yuewen_revised != "":
                if yuewen_revised == yuewen:
                    raise ValueError(yuewen_unmodified_error.format(idx + 1))
                if note == "":
                    raise ValueError(
                        yuewen_revised_provided_note_missing_error.format(idx + 1)
                    )
            elif note != "":
                raise ValueError(
                    yuewen_revised_missing_note_provided_error.format(idx + 1)
                )
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[ReviewPrompt2] = ReviewPrompt2,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        query_cls = ReviewQuery2.get_query_cls(size)
        answer_cls = ReviewAnswer2.get_answer_cls(size)
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
        size = sum(1 for key in data["query"] if key.startswith("zhongwen_"))
        test_case_cls = cls.get_test_case_cls(size=size, **kwargs)
        return test_case_cls
