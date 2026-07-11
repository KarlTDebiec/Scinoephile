#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM managers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model, model_validator

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
    test_case_base_cls: ClassVar[type[TestCase]] = TestCase
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
        fields = cls.get_test_case_fields(query_cls, answer_cls, prompt)
        validators = cls.get_test_case_validators()

        model = create_model(
            get_model_name(cls.test_case_base_cls.__name__, prompt.name),
            __base__=cls.test_case_base_cls,
            __module__=cls.test_case_base_cls.__module__,
            __validators__=validators,
            **fields,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt = prompt
        setattr(model, "get_auto_verified", cls.get_auto_verified)
        setattr(model, "get_min_difficulty", cls.get_min_difficulty)
        return model

    @classmethod
    def get_test_case_fields(
        cls,
        query_cls: type[Query],
        answer_cls: type[Answer],
        prompt: Prompt,
    ) -> dict[str, Any]:
        """Get fields dictionary for dynamic TestCase class creation.

        Arguments:
            query_cls: query model class
            answer_cls: answer model class
            prompt: text for LLM correspondence
        Returns:
            fields dictionary for create_model
        """
        fields: dict[str, Any] = {
            "query": (query_cls, Field(...)),
            "answer": (answer_cls | None, Field(default=None)),
            "difficulty": (
                int,
                Field(0, description=prompt.difficulty_description),
            ),
            "few_shot": (
                bool,
                Field(False, description=prompt.few_shot_description),
            ),
            "verified": (
                bool,
                Field(False, description=prompt.verified_description),
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
        """Ensure difficulty reflects few-shot/split status if not already higher.

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
