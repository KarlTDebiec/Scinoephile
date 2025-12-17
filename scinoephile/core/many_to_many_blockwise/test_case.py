#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for many-to-many blockwise test cases."""

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
    """ABC for many-to-many blockwise test cases."""

    answer_cls: ClassVar[type[ManyToManyBlockwiseAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[ManyToManyBlockwiseQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[ManyToManyBlockwisePrompt]]
    """Text for LLM correspondence."""

    size: ClassVar[int]
    """Number of subtitles."""

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        if self.answer is None:
            return self

        for idx in range(self.size):
            source_one = getattr(self.query, self.prompt_cls.source_one(idx + 1))
            output = getattr(self.answer, self.prompt_cls.output(idx + 1))
            note = getattr(self.answer, self.prompt_cls.note(idx + 1))
            if output != "":
                if output == source_one:
                    raise ValueError(
                        self.prompt_cls.output_present_but_unmodified_err(idx + 1)
                    )
                if note == "":
                    raise ValueError(
                        self.prompt_cls.output_present_note_missing_err(idx + 1)
                    )
            elif note != "":
                raise ValueError(
                    self.prompt_cls.output_missing_note_present_err(idx + 1)
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
            prompt_cls: text for LLM correspondence
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
        prompt_cls: type[ManyToManyBlockwisePrompt] = kwargs.get(
            "prompt_cls", ManyToManyBlockwisePrompt
        )
        size = sum(
            1 for key in data["query"] if key.startswith(prompt_cls.source_one_pfx)
        )
        return cls.get_test_case_cls(size=size, prompt_cls=prompt_cls)
