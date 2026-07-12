#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific delineation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .models import DelineationAnswer, DelineationQuery, DelineationTestCase
from .prompt import DelineationPrompt

__all__ = ["DelineationManager"]


class DelineationManager(Manager):
    """Factories for prompt-specific delineation LLM classes."""

    operation: ClassVar[str] = "delineation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[DelineationPrompt] = DelineationPrompt()
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = DelineationTestCase
    """Static test-case model defining delineation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt: DelineationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        fields: dict[str, Any] = {
            "output_one": (
                str,
                Field(
                    "",
                    alias=prompt.src_2_sub_1_shifted,
                    description=prompt.src_2_sub_1_shifted_desc,
                ),
            ),
            "output_two": (
                str,
                Field(
                    "",
                    alias=prompt.src_2_sub_2_shifted,
                    description=prompt.src_2_sub_2_shifted_desc,
                ),
            ),
        }
        model = create_model(
            get_model_name("DelineationAnswer", prompt.name),
            __base__=DelineationAnswer,
            __module__=DelineationAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt: DelineationPrompt,
    ) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        fields: dict[str, Any] = {
            "reference_one": (
                str,
                Field(
                    ...,
                    alias=prompt.src_1_sub_1,
                    description=prompt.src_1_sub_1_desc,
                ),
            ),
            "reference_two": (
                str,
                Field(
                    ...,
                    alias=prompt.src_1_sub_2,
                    description=prompt.src_1_sub_2_desc,
                ),
            ),
            "target_one": (
                str,
                Field(
                    "",
                    alias=prompt.src_2_sub_1,
                    description=prompt.src_2_sub_1_desc,
                ),
            ),
            "target_two": (
                str,
                Field(
                    "",
                    alias=prompt.src_2_sub_2,
                    description=prompt.src_2_sub_2_desc,
                ),
            ),
        }
        model = create_model(
            get_model_name("DelineationQuery", prompt.name),
            __base__=DelineationQuery,
            __module__=DelineationQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model
