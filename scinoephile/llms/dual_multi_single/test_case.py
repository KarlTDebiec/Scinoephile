#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual track / multi-subtitle single subtitle test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import create_model

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import TestCase
from scinoephile.llms.base.models import get_model_name

from .answer import DualMultiSingleAnswer
from .prompt import DualMultiSinglePrompt
from .query import DualMultiSingleQuery

__all__ = ["DualMultiSingleTestCase"]


class DualMultiSingleTestCase(TestCase, ABC):
    """ABC for dual track / multi-subtitle single subtitle test cases."""

    answer_cls: ClassVar[type[DualMultiSingleAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[DualMultiSingleQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[DualMultiSinglePrompt]]
    """Text for LLM correspondence."""

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[DualMultiSinglePrompt],
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = DualMultiSingleQuery.get_query_cls(prompt_cls)
        answer_cls = DualMultiSingleAnswer.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data from JSON
            **kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case class
        """
        if (prompt_cls := kwargs.get("prompt_cls")) is None:
            raise ScinoephileError("prompt_cls must be provided as a keyword argument")
        return cls.get_test_case_cls(prompt_cls=prompt_cls)
