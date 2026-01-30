#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM managers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, TypedDict, Unpack

from pydantic import Field, create_model, model_validator

from scinoephile.core import ScinoephileError

from .answer import Answer
from .models import get_model_name
from .prompt import Prompt
from .query import Query
from .test_case import TestCase

__all__ = [
    "Manager",
    "TestCaseClsKwargs",
]


class TestCaseClsKwargs(TypedDict, total=False):
    """Keyword arguments for Manager.get_test_case_cls_from_data."""

    prompt_cls: type[Prompt]
    manager_cls: type[Manager]


class Manager(ABC):
    """ABC for LLM managers."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[Prompt],
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        raise NotImplementedError

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[Prompt],
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        raise NotImplementedError

    @classmethod
    @cache
    def get_test_case_cls[TTestCase: TestCase](
        cls,
        prompt_cls: type[Prompt],
    ) -> type[TTestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            test case model class
        """
        query_cls = cls.get_query_cls(prompt_cls)
        answer_cls = cls.get_answer_cls(prompt_cls)
        fields = cls.get_test_case_fields(query_cls, answer_cls, prompt_cls)
        validators = cls.get_test_case_validators()

        model = create_model(
            get_model_name(TestCase.__name__, prompt_cls.__name__),
            __base__=TestCase,
            __module__=TestCase.__module__,
            __validators__=validators,
            **fields,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        model.get_auto_verified = cls.get_auto_verified
        model.get_min_difficulty = cls.get_min_difficulty
        return model

    @classmethod
    def get_test_case_cls_from_data[TTestCase: TestCase](
        cls,
        data: dict,
        **kwargs: Unpack[TestCaseClsKwargs],
    ) -> type[TTestCase]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data from JSON
            **kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case class
        """
        if (prompt_cls := kwargs.get("prompt_cls")) is None:
            raise ScinoephileError("prompt_cls must be provided as a keyword argument")
        manager_cls = kwargs.get("manager_cls") or cls
        return manager_cls.get_test_case_cls(prompt_cls=prompt_cls)

    @classmethod
    def get_test_case_fields(
        cls,
        query_cls: type[Query],
        answer_cls: type[Answer],
        prompt_cls: type[Prompt],
    ) -> dict[str, Any]:
        """Get fields dictionary for dynamic TestCase class creation.

        Arguments:
            query_cls: query model class
            answer_cls: answer model class
            prompt_cls: text for LLM correspondence
        Returns:
            fields dictionary for create_model
        """
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
        return fields

    @classmethod
    def get_test_case_validators(cls) -> dict[str, Any]:
        """Get validators dictionary for dynamic TestCase class creation.

        Returns:
            validators dictionary for create_model
        """
        validators: dict[str, Any] = {
            "enforce_min_difficulty": model_validator(mode="after")(
                cls.enforce_min_difficulty
            ),
            "validate_test_case": model_validator(mode="after")(cls.validate_test_case),
        }
        return validators

    @staticmethod
    def enforce_min_difficulty(model: TestCase) -> TestCase:
        """Ensure difficulty reflects prompt/split status if not already higher.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        model.difficulty = max(model.difficulty, model.get_min_difficulty())
        return model

    @staticmethod
    def get_auto_verified(model: TestCase) -> bool:
        """Whether this test case should automatically be verified.

        Arguments:
            model: test case to inspect
        Returns:
            whether the test case should be auto-verified
        """
        return False

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        return 0

    @staticmethod
    def validate_query(model: Query) -> Query:
        """Ensure query is valid.

        Arguments:
            model: query to validate
        Returns:
            validated query
        """
        return model

    @staticmethod
    def validate_answer(model: Answer) -> Answer:
        """Ensure answer is valid.

        Arguments:
            model: answer to validate
        Returns:
            validated answer
        """
        return model

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure query and answer together are valid.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        return model
