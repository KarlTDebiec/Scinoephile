#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription review test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.models import get_model_name

from .answer import ManyToManyBlockwiseAnswer
from .prompt import ManyToManyBlockwisePrompt
from .query import ManyToManyBlockwiseQuery

__all__ = ["ManyToManyBlockwiseTestCase"]


class ManyToManyBlockwiseTestCase(TestCase, ABC):
    """Abstract base class for 粤文 transcription review test cases."""

    answer_cls: ClassVar[type[ManyToManyBlockwiseAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ManyToManyBlockwiseQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ManyToManyBlockwisePrompt]]
    """Text strings to be used for corresponding with LLM."""

    size: ClassVar[int]
    """Number of subtitles."""

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        for idx in range(self.size):
            yuewen = getattr(self.query, self.prompt_cls.yuewen_field(idx + 1))
            yuewen_revised = getattr(
                self.answer, self.prompt_cls.yuewen_revised_field(idx + 1)
            )
            note = getattr(self.answer, self.prompt_cls.note(idx + 1))
            if yuewen_revised != "":
                if yuewen_revised == yuewen:
                    raise ValueError(self.prompt_cls.yuewen_unmodified_error(idx + 1))
                if note == "":
                    raise ValueError(
                        self.prompt_cls.yuewen_revised_provided_note_missing_err(
                            idx + 1
                        )
                    )
            elif note != "":
                raise ValueError(
                    self.prompt_cls.yuewen_revised_missing_note_provided_error(idx + 1)
                )
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        prompt_cls: type[ManyToManyBlockwisePrompt] = ManyToManyBlockwisePrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, f"{size}_{prompt_cls.__name__}")
        query_cls = ManyToManyBlockwiseQuery.get_query_cls(size, prompt_cls)
        answer_cls = ManyToManyBlockwiseAnswer.get_answer_cls(size, prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

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
            data: data from JSON
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            TestCase type with appropriate configuration
        """
        prompt_cls = kwargs.get("prompt_cls", ManyToManyBlockwisePrompt)
        size = sum(
            1 for key in data["query"] if key.startswith(prompt_cls.zhongwen_prefix)
        )
        return cls.get_test_case_cls(size=size, prompt_cls=prompt_cls)
