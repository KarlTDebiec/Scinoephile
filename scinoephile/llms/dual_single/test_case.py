#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual track / single subtitle test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model

from scinoephile.llms.base import TestCase
from scinoephile.llms.base.models import get_model_name

from .answer import DualSingleAnswer
from .prompt import DualSinglePrompt
from .query import DualSingleQuery

__all__ = ["DualSingleTestCase"]


class DualSingleTestCase(TestCase, ABC):
    """ABC for dual track / single subtitle test cases."""

    answer_cls: ClassVar[type[DualSingleAnswer]] = DualSingleAnswer
    """Answer class for this test case."""
    query_cls: ClassVar[type[DualSingleQuery]] = DualSingleQuery
    """Query class for this test case."""
    prompt_cls: ClassVar[type[DualSinglePrompt]]
    """Text for LLM correspondence."""

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        prompt_cls: type[DualSinglePrompt],
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        name = get_model_name(cls.__name__, prompt_cls.__name__)
        query_cls = cls.query_cls.get_query_cls(prompt_cls)
        answer_cls = cls.answer_cls.get_answer_cls(prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        return model
