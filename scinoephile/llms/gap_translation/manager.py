#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific gap-translation LLM classes."""

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
    GapTranslationAnswer,
    GapTranslationQuery,
    GapTranslationSubtitle,
    GapTranslationTestCase,
)
from .prompt import GapTranslationPrompt

__all__ = ["GapTranslationManager"]


class GapTranslationManager(Manager[GapTranslationTestCase]):
    """Factories for prompt-specific gap-translation LLM classes."""

    operation: ClassVar[str] = "gap-translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GapTranslationPrompt] = GapTranslationTestCase.prompt
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = GapTranslationTestCase
    """Static test-case model defining gap translation's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: GapTranslationPrompt) -> type[Answer]:
        """Get answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        output_cls = cls.get_output_cls(prompt)
        return cls.create_prompt_model(
            GapTranslationAnswer,
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
        prompt: GapTranslationPrompt,
    ) -> type[GapTranslationSubtitle]:
        """Get guide class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            guide model class
        """
        return cls.create_prompt_model(
            GapTranslationSubtitle,
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
            name="GapTranslationGuide",
        )

    @classmethod
    @cache
    def get_output_cls(
        cls,
        prompt: GapTranslationPrompt,
    ) -> type[GapTranslationSubtitle]:
        """Get output class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            output model class
        """
        return cls.create_prompt_model(
            GapTranslationSubtitle,
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
            name="GapTranslationOutput",
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: GapTranslationPrompt) -> type[Query]:
        """Get query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        target_cls = cls.get_target_cls(prompt)
        guide_cls = cls.get_guide_cls(prompt)
        return cls.create_prompt_model(
            GapTranslationQuery,
            prompt,
            {
                "targets": PromptModelField(
                    alias=prompt.targets,
                    annotation=list[target_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.targets_desc,
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
    def get_target_cls(
        cls,
        prompt: GapTranslationPrompt,
    ) -> type[GapTranslationSubtitle]:
        """Get target class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            target model class
        """
        return cls.create_prompt_model(
            GapTranslationSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index,
                    description=prompt.index_desc,
                ),
                "text": PromptModelField(
                    alias=prompt.text,
                    description=prompt.target_text_desc,
                ),
            },
            name="GapTranslationTarget",
        )
