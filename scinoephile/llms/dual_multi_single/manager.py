#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for dual track / multi-subtitle LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar, Unpack

from pydantic import Field, create_model, model_validator

from scinoephile.llms.base import Answer, Manager, Query, TestCase, TestCaseClsKwargs
from scinoephile.llms.base.models import get_model_name

from .prompt import DualMultiSinglePrompt

__all__ = ["DualMultiSingleManager"]


class DualMultiSingleManager(Manager):
    """Factories for dual track / multi-subtitle LLM classes."""

    prompt_cls: ClassVar[type[DualMultiSinglePrompt]] = DualMultiSinglePrompt
    """Default prompt class."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[DualMultiSinglePrompt] = DualMultiSinglePrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("DualMultiSingleQuery", prompt_cls.__name__)
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
        prompt_cls: type[DualMultiSinglePrompt] = DualMultiSinglePrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("DualMultiSingleAnswer", prompt_cls.__name__)
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
        source_one = getattr(model, model.prompt_cls.src_1, None)
        source_two = getattr(model, model.prompt_cls.src_2, None)
        if not source_one:
            raise ValueError(model.prompt_cls.src_1_missing_err)
        if not source_two:
            raise ValueError(model.prompt_cls.src_2_missing_err)
        return model

    @staticmethod
    def validate_answer(model: Answer) -> Answer:
        """Ensure answer is internally valid.

        Arguments:
            model: answer to validate
        Returns:
            validated answer
        """
        output = getattr(model, model.prompt_cls.output, None)
        if not output:
            raise ValueError(model.prompt_cls.output_missing_err)
        return model
