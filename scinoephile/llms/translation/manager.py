#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific translation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import (
    Answer,
    Manager,
    Query,
    TestCase,
    TestCaseSubtitle,
)
from scinoephile.core.llms.models import get_model_name

from .models import (
    TranslationAnswer,
    TranslationOutput,
    TranslationQuery,
    TranslationTestCase,
)
from .prompt import TranslationPrompt

__all__ = ["TranslationManager"]


class TranslationManager(Manager):
    """Factories for prompt-specific translation LLM classes."""

    operation: ClassVar[str] = "translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[TranslationPrompt] = TranslationPrompt()
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = TranslationTestCase
    """Static test-case model defining translation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: TranslationPrompt) -> type[Answer]:
        """Get concrete answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        output_cls = cls.get_output_cls(prompt)
        fields: dict[str, Any] = {
            "outputs": (
                list[output_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.outputs,
                    description=prompt.outputs_desc,
                    min_length=1,
                ),
            ),
        }
        model = create_model(
            get_model_name("TranslationAnswer", prompt.name),
            __base__=TranslationAnswer,
            __module__=TranslationAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_output_cls(cls, prompt: TranslationPrompt) -> type[TranslationOutput]:
        """Get output class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            output model class
        """
        fields: dict[str, Any] = {
            "index": (
                int,
                Field(
                    ...,
                    alias=prompt.index,
                    description=prompt.index_desc,
                    ge=1,
                ),
            ),
            "text": (
                str,
                Field(
                    ...,
                    alias=prompt.text,
                    description=prompt.output_text_desc,
                ),
            ),
        }
        return create_model(
            get_model_name("TranslationOutput", prompt.name),
            __base__=TranslationOutput,
            __module__=TranslationAnswer.__module__,
            **fields,
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: TranslationPrompt) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        subtitle_cls = cls.get_subtitle_cls(prompt)
        fields: dict[str, Any] = {
            "subtitles": (
                list[subtitle_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.subtitles,
                    description=prompt.subtitles_desc,
                    min_length=1,
                ),
            ),
        }
        model = create_model(
            get_model_name("TranslationQuery", prompt.name),
            __base__=TranslationQuery,
            __module__=TranslationQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_subtitle_cls(cls, prompt: TranslationPrompt) -> type[TestCaseSubtitle]:
        """Get subtitle class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            subtitle model class
        """
        fields: dict[str, Any] = {
            "index": (
                int,
                Field(
                    ...,
                    alias=prompt.index,
                    description=prompt.index_desc,
                    ge=1,
                ),
            ),
            "text": (
                str,
                Field(
                    ...,
                    alias=prompt.text,
                    description=prompt.subtitle_text_desc,
                    max_length=1000,
                ),
            ),
        }
        return create_model(
            get_model_name("TranslationSubtitle", prompt.name),
            __base__=TestCaseSubtitle,
            __module__=TranslationQuery.__module__,
            **fields,
        )
