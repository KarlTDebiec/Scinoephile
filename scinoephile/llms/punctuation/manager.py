#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for punctuation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .models import PunctuationAnswer, PunctuationQuery, PunctuationTestCase
from .prompt import PunctuationPrompt

__all__ = ["PunctuationManager"]


class PunctuationManager(Manager):
    """Factories for punctuation LLM classes."""

    operation: ClassVar[str] = "punctuation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[PunctuationPrompt] = PunctuationPrompt()
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = PunctuationTestCase
    """Static test-case model defining punctuation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt: PunctuationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        fields: dict[str, Any] = {
            "output": (
                str,
                Field(
                    ...,
                    alias=prompt.output,
                    description=prompt.output_desc,
                ),
            ),
        }
        model = create_model(
            get_model_name("PunctuationAnswer", prompt.name),
            __base__=PunctuationAnswer,
            __module__=PunctuationAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt: PunctuationPrompt,
    ) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        fields: dict[str, Any] = {
            "subtitles": (
                list[str],
                Field(
                    ...,
                    alias=prompt.src_1,
                    description=prompt.src_1_desc,
                ),
            ),
            "guide": (
                str,
                Field(
                    ...,
                    alias=prompt.src_2,
                    description=prompt.src_2_desc,
                ),
            ),
        }
        model = create_model(
            get_model_name("PunctuationQuery", prompt.name),
            __base__=PunctuationQuery,
            __module__=PunctuationQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model
