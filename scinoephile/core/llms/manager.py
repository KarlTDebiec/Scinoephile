#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM managers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from .answer import Answer
from .models import get_model_name
from .prompt import Prompt
from .query import Query
from .test_case import TestCase

__all__ = ["Manager"]


class Manager(ABC):
    """ABC for LLM managers."""

    operation: ClassVar[str]
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[Prompt]
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]]
    """Static test-case model defining the operation's semantic shape."""

    @classmethod
    def get_query_cls(cls, prompt: Prompt) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        raise NotImplementedError

    @classmethod
    def get_answer_cls(cls, prompt: Prompt) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        raise NotImplementedError

    @classmethod
    @cache
    def get_test_case_cls(cls, prompt: Prompt) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            test case model class
        """
        query_cls = cls.get_query_cls(prompt)
        answer_cls = cls.get_answer_cls(prompt)
        fields = cls.get_test_case_fields(query_cls, answer_cls)

        model = create_model(
            get_model_name(cls.test_case_base_cls.__name__, prompt.name),
            __base__=cls.test_case_base_cls,
            __module__=cls.test_case_base_cls.__module__,
            **fields,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt = prompt
        return model

    @classmethod
    def get_test_case_fields(
        cls,
        query_cls: type[Query],
        answer_cls: type[Answer],
    ) -> dict[str, Any]:
        """Get fields dictionary for dynamic TestCase class creation.

        Arguments:
            query_cls: query model class
            answer_cls: answer model class
        Returns:
            fields dictionary for create_model
        """
        fields: dict[str, Any] = {
            "query": (query_cls, Field(...)),
            "answer": (answer_cls | None, Field(default=None)),
        }
        return fields
