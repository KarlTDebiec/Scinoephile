#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for dual n to 1 LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar, Unpack

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Answer, Manager, Query, TestCase, TestCaseClsKwargs
from scinoephile.core.llms.models import get_model_name

from .prompt import DualNTo1Prompt

__all__ = ["DualNTo1Manager"]


class DualNTo1Manager(Manager):
    """Factories for dual n to 1 LLM classes."""

    prompt_cls: ClassVar[type[DualNTo1Prompt]] = DualNTo1Prompt
    """Default prompt class."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[DualNTo1Prompt] = DualNTo1Prompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("DualNTo1Query", prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.src_1: (
                list[str],
                Field(..., description=prompt_cls.src_1_desc),
            ),
            prompt_cls.src_2: (
                str,
                Field(..., description=prompt_cls.src_2_desc),
            ),
        }

        validators: dict[str, Any] = {
            "validate_query": model_validator(mode="after")(cls.validate_query),
        }

        model = create_model(
            name,
            __base__=Query,
            __module__=Query.__module__,
            __validators__=validators,
            **fields,
        )
        model.prompt_cls = prompt_cls
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[DualNTo1Prompt] = DualNTo1Prompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("DualNTo1Answer", prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.output: (
                str,
                Field(..., description=prompt_cls.output_desc),
            ),
        }

        validators: dict[str, Any] = {
            "validate_answer": model_validator(mode="after")(cls.validate_answer),
        }

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            __validators__=validators,
            **fields,
        )
        model.prompt_cls = prompt_cls
        return model

    @classmethod
    def get_test_case_cls_from_data(
        cls,
        data: dict,
        **kwargs: Unpack[TestCaseClsKwargs],
    ) -> type[TestCase]:
        """Get concrete test case class for provided data.

        Arguments:
            data: data from JSON
            **kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case model class
        """
        prompt_cls = kwargs.get("prompt_cls") or cls.prompt_cls
        return cls.get_test_case_cls(prompt_cls=prompt_cls)

    @staticmethod
    def validate_query(model: Query) -> Query:
        """Ensure query is internally valid.

        Arguments:
            model: query to validate
        Returns:
            validated query
        """
        prompt_cls: type[DualNTo1Prompt] = getattr(model, "prompt_cls")
        source_one = getattr(model, prompt_cls.src_1, None)
        source_two = getattr(model, prompt_cls.src_2, None)
        if not source_one:
            raise ValueError(prompt_cls.src_1_missing_err)
        if not source_two:
            raise ValueError(prompt_cls.src_2_missing_err)
        return model

    @staticmethod
    def validate_answer(model: Answer) -> Answer:
        """Ensure answer is internally valid.

        Arguments:
            model: answer to validate
        Returns:
            validated answer
        """
        prompt_cls: type[DualNTo1Prompt] = getattr(model, "prompt_cls")
        output = getattr(model, prompt_cls.output, None)
        if not output:
            raise ValueError(prompt_cls.output_missing_err)
        return model
