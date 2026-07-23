#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific translation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import (
    Answer,
    Manager,
    PromptModelField,
    Query,
    TestCase,
    TestCaseSubtitle,
)

from .models import (
    TranslationAnswer,
    TranslationOutput,
    TranslationQuery,
    TranslationTestCase,
)
from .prompt import TranslationPrompt

__all__ = ["TranslationManager"]


class TranslationManager(Manager[TranslationTestCase]):
    """Factories for prompt-specific translation LLM classes."""

    operation: ClassVar[str] = "translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[TranslationPrompt] = TranslationTestCase.prompt
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
        return cls.create_prompt_model(
            TranslationAnswer,
            prompt,
            {
                "outputs": PromptModelField(
                    alias=prompt.outputs,
                    annotation=list[output_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.outputs_desc,
                ),
            },
        )

    @classmethod
    @cache
    def get_output_cls(cls, prompt: TranslationPrompt) -> type[TranslationOutput]:
        """Get output class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            output model class
        """
        return cls.create_prompt_model(
            TranslationOutput,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index,
                    description=prompt.index_desc,
                ),
                "text": PromptModelField(
                    alias=prompt.text,
                    description=prompt.output_text_desc,
                ),
            },
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
        return cls.create_prompt_model(
            TranslationQuery,
            prompt,
            {
                "subtitles": PromptModelField(
                    alias=prompt.subtitles,
                    annotation=list[subtitle_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.subtitles_desc,
                ),
            },
        )

    @classmethod
    @cache
    def get_subtitle_cls(cls, prompt: TranslationPrompt) -> type[TestCaseSubtitle]:
        """Get subtitle class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            subtitle model class
        """
        return cls.create_prompt_model(
            TestCaseSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index,
                    description=prompt.index_desc,
                ),
                "text": PromptModelField(
                    alias=prompt.text,
                    description=prompt.subtitle_text_desc,
                ),
            },
            module=TranslationQuery.__module__,
            name="TranslationSubtitle",
        )
