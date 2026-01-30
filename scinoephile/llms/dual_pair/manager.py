#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for dual track / subtitle pair LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model, model_validator

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import Answer, Manager, Query, TestCase
from scinoephile.llms.base.models import get_model_name

from .prompt import DualPairPrompt

__all__ = ["DualPairManager"]


class DualPairManager(Manager):
    """Factories for dual track / subtitle pair LLM classes."""

    prompt_cls: ClassVar[type[DualPairPrompt]] = DualPairPrompt
    """Default prompt class."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[DualPairPrompt] = DualPairPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("DualPairQuery", prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.src_1_sub_1: (
                str,
                Field(..., description=prompt_cls.src_1_sub_1_desc),
            ),
            prompt_cls.src_1_sub_2: (
                str,
                Field(..., description=prompt_cls.src_1_sub_2_desc),
            ),
            prompt_cls.src_2_sub_1: (
                str,
                Field("", description=prompt_cls.src_2_sub_1_desc),
            ),
            prompt_cls.src_2_sub_2: (
                str,
                Field("", description=prompt_cls.src_2_sub_2_desc),
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
        prompt_cls: type[DualPairPrompt] = DualPairPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("DualPairAnswer", prompt_cls.__name__)
        fields: dict[str, Any] = {
            prompt_cls.src_2_sub_1_shifted: (
                str,
                Field("", description=prompt_cls.src_2_sub_1_shifted_desc),
            ),
            prompt_cls.src_2_sub_2_shifted: (
                str,
                Field("", description=prompt_cls.src_2_sub_2_shifted_desc),
            ),
        }

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        return model

    @classmethod
    def get_test_case_cls_from_data(
        cls,
        data: dict,
        **kwargs: Any,
    ) -> type[TestCase]:
        """Get concrete test case class for provided data.

        Arguments:
            data: data from JSON
            **kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case model class
        """
        if (prompt_cls := kwargs.get("prompt_cls")) is None:
            raise ScinoephileError("prompt_cls must be provided as a keyword argument")
        return cls.get_test_case_cls(prompt_cls=prompt_cls)

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        min_difficulty = 0
        if model.answer is None:
            return min_difficulty

        target_1_shifted = getattr(
            model.answer, model.prompt_cls.src_2_sub_1_shifted, None
        )
        target_2_shifted = getattr(
            model.answer, model.prompt_cls.src_2_sub_2_shifted, None
        )
        if target_1_shifted != "" or target_2_shifted != "":
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @staticmethod
    def validate_query(model: Query) -> Query:
        """Ensure query is internally valid.

        Arguments:
            model: query to validate
        Returns:
            validated query
        """
        src_2_sub_1 = getattr(model, model.prompt_cls.src_2_sub_1, None)
        src_2_sub_2 = getattr(model, model.prompt_cls.src_2_sub_2, None)
        if not src_2_sub_1 and not src_2_sub_2:
            raise ValueError(model.prompt_cls.src_2_sub_1_sub_2_missing_err)
        return model

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure query and answer together are valid.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        if model.answer is None:
            return model

        target_1 = getattr(model.query, model.prompt_cls.src_2_sub_1, "")
        target_2 = getattr(model.query, model.prompt_cls.src_2_sub_2, "")
        target_1_shifted = getattr(
            model.answer, model.prompt_cls.src_2_sub_1_shifted, ""
        )
        target_2_shifted = getattr(
            model.answer, model.prompt_cls.src_2_sub_2_shifted, ""
        )
        if target_1 == target_1_shifted and target_2 == target_2_shifted:
            raise ValueError(model.prompt_cls.src_2_sub_1_sub_2_unchanged_err)
        if target_1_shifted != "" or target_2_shifted != "":
            expected = target_1 + target_2
            received = target_1_shifted + target_2_shifted
            if expected != received:
                raise ValueError(
                    model.prompt_cls.src_2_chars_changed_err(expected, received)
                )
        return model
