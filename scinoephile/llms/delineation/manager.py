#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for delineation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .prompt import DelineationPrompt

__all__ = ["DelineationManager"]


class DelineationManager(Manager):
    """Factories for delineation LLM classes."""

    operation: ClassVar[str] = "delineation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[DelineationPrompt] = DelineationPrompt()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt: DelineationPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        name = get_model_name("DelineationQuery", prompt.name)
        fields: dict[str, Any] = {
            prompt.src_1_sub_1: (
                str,
                Field(..., description=prompt.src_1_sub_1_desc),
            ),
            prompt.src_1_sub_2: (
                str,
                Field(..., description=prompt.src_1_sub_2_desc),
            ),
            prompt.src_2_sub_1: (
                str,
                Field("", description=prompt.src_2_sub_1_desc),
            ),
            prompt.src_2_sub_2: (
                str,
                Field("", description=prompt.src_2_sub_2_desc),
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
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt: DelineationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        name = get_model_name("DelineationAnswer", prompt.name)
        fields: dict[str, Any] = {
            prompt.src_2_sub_1_shifted: (
                str,
                Field("", description=prompt.src_2_sub_1_shifted_desc),
            ),
            prompt.src_2_sub_2_shifted: (
                str,
                Field("", description=prompt.src_2_sub_2_shifted_desc),
            ),
        }

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on the test case properties.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        prompt: DelineationPrompt = getattr(model, "prompt")
        min_difficulty = 0
        if model.answer is None:
            return min_difficulty

        target_1_shifted = getattr(model.answer, prompt.src_2_sub_1_shifted, None)
        target_2_shifted = getattr(model.answer, prompt.src_2_sub_2_shifted, None)
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
        prompt: DelineationPrompt = getattr(model, "prompt")
        src_2_sub_1 = getattr(model, prompt.src_2_sub_1, None)
        src_2_sub_2 = getattr(model, prompt.src_2_sub_2, None)
        if not src_2_sub_1 and not src_2_sub_2:
            raise ValueError(prompt.src_2_sub_1_sub_2_missing_err)
        return model

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure query and answer together are valid.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        prompt: DelineationPrompt = getattr(model, "prompt")
        if model.answer is None:
            return model

        target_1 = getattr(model.query, prompt.src_2_sub_1, "")
        target_2 = getattr(model.query, prompt.src_2_sub_2, "")
        target_1_shifted = getattr(model.answer, prompt.src_2_sub_1_shifted, "")
        target_2_shifted = getattr(model.answer, prompt.src_2_sub_2_shifted, "")
        if target_1 == target_1_shifted and target_2 == target_2_shifted:
            raise ValueError(prompt.src_2_sub_1_sub_2_unchanged_err)
        if target_1_shifted != "" or target_2_shifted != "":
            expected = target_1 + target_2
            received = target_1_shifted + target_2_shifted
            if expected != received:
                raise ValueError(prompt.src_2_chars_changed_err(expected, received))
        return model
