#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific guided-translation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import (
    Answer,
    Manager,
    PromptModelField,
    Query,
    TestCase,
)

from .models import (
    GuidedTranslationAnswer,
    GuidedTranslationQuery,
    GuidedTranslationSubtitle,
    GuidedTranslationTestCase,
)
from .prompt import GuidedTranslationPrompt

__all__ = ["GuidedTranslationManager"]


class GuidedTranslationManager(Manager[GuidedTranslationTestCase]):
    """Factories for prompt-specific guided-translation LLM classes."""

    operation: ClassVar[str] = "guided-translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GuidedTranslationPrompt] = GuidedTranslationTestCase.prompt
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
        return cls.create_prompt_model(
            GuidedTranslationAnswer,
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
        return cls.create_prompt_model(
            GuidedTranslationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index,
                    description=prompt.index_desc,
                ),
                "text": PromptModelField(
                    alias=prompt.text,
                    description=prompt.guide_text_desc,
                ),
            },
            name="GuidedTranslationGuide",
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
        return cls.create_prompt_model(
            GuidedTranslationSubtitle,
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
            name="GuidedTranslationOutput",
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
        return cls.create_prompt_model(
            GuidedTranslationQuery,
            prompt,
            {
                "subtitles": PromptModelField(
                    alias=prompt.subtitles,
                    annotation=list[subtitle_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.subtitles_desc,
                ),
                "guides": PromptModelField(
                    alias=prompt.guides,
                    annotation=list[guide_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.guides_desc,
                ),
            },
        )

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
        return cls.create_prompt_model(
            GuidedTranslationSubtitle,
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
        )
