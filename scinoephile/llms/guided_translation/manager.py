#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific guided-translation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import (
    Answer,
    Manager,
    Query,
    TestCase,
)
from scinoephile.core.llms.models import get_model_name

from .models import (
    GuidedTranslationAnswer,
    GuidedTranslationQuery,
    GuidedTranslationSubtitle,
    GuidedTranslationTestCase,
)
from .prompt import GuidedTranslationPrompt

__all__ = ["GuidedTranslationManager"]


class GuidedTranslationManager(Manager):
    """Factories for prompt-specific guided-translation LLM classes."""

    operation: ClassVar[str] = "guided-translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GuidedTranslationPrompt] = GuidedTranslationPrompt()
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = GuidedTranslationTestCase
    """Static test-case model defining guided translation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: GuidedTranslationPrompt) -> type[Answer]:
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
            get_model_name("GuidedTranslationAnswer", prompt.name),
            __base__=GuidedTranslationAnswer,
            __module__=GuidedTranslationAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_guide_cls(
        cls,
        prompt: GuidedTranslationPrompt,
    ) -> type[GuidedTranslationSubtitle]:
        """Get guide-item class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            guide-item model class
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
                    description=prompt.guide_text_desc,
                ),
            ),
        }
        return create_model(
            get_model_name("GuidedTranslationGuide", prompt.name),
            __base__=GuidedTranslationSubtitle,
            __module__=GuidedTranslationQuery.__module__,
            **fields,
        )

    @classmethod
    @cache
    def get_output_cls(
        cls,
        prompt: GuidedTranslationPrompt,
    ) -> type[GuidedTranslationSubtitle]:
        """Get output-item class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            output-item model class
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
            get_model_name("GuidedTranslationOutput", prompt.name),
            __base__=GuidedTranslationSubtitle,
            __module__=GuidedTranslationAnswer.__module__,
            **fields,
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: GuidedTranslationPrompt) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        subtitle_cls = cls.get_subtitle_cls(prompt)
        guide_cls = cls.get_guide_cls(prompt)
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
            "guides": (
                list[guide_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.guides,
                    description=prompt.guides_desc,
                ),
            ),
        }
        model = create_model(
            get_model_name("GuidedTranslationQuery", prompt.name),
            __base__=GuidedTranslationQuery,
            __module__=GuidedTranslationQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_subtitle_cls(
        cls,
        prompt: GuidedTranslationPrompt,
    ) -> type[GuidedTranslationSubtitle]:
        """Get subtitle-item class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            subtitle-item model class
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
                ),
            ),
        }
        return create_model(
            get_model_name("GuidedTranslationSubtitle", prompt.name),
            __base__=GuidedTranslationSubtitle,
            __module__=GuidedTranslationQuery.__module__,
            **fields,
        )
