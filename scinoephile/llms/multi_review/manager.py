#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific multi-review LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import Answer, Manager, PromptModelField, Query, TestCase

from .models import (
    MultiReviewAnswer,
    MultiReviewQuery,
    MultiReviewSource,
    MultiReviewSubtitle,
    MultiReviewTestCase,
)
from .prompt import MultiReviewPrompt

__all__ = ["MultiReviewManager"]


class MultiReviewManager(Manager[MultiReviewTestCase]):
    """Factories for prompt-specific multi-review LLM classes."""

    operation: ClassVar[str] = "multi-review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[MultiReviewPrompt] = MultiReviewTestCase.prompt
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = MultiReviewTestCase
    """Static test-case model defining multi-review's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: MultiReviewPrompt) -> type[Answer]:
        """Get concrete answer class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        output_cls = cls.get_output_cls(prompt)
        return cls.create_prompt_model(
            MultiReviewAnswer,
            prompt,
            {
                "outputs": PromptModelField(
                    alias=prompt.outputs,
                    annotation=list[output_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.outputs_desc,
                )
            },
        )

    @classmethod
    @cache
    def get_guide_cls(cls, prompt: MultiReviewPrompt) -> type[MultiReviewSubtitle]:
        """Get guide-item class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            guide-item model class
        """
        return cls.create_prompt_model(
            MultiReviewSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.guide_text_desc
                ),
            },
            name="MultiReviewGuide",
        )

    @classmethod
    @cache
    def get_output_cls(cls, prompt: MultiReviewPrompt) -> type[MultiReviewSubtitle]:
        """Get output-item class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            output-item model class
        """
        return cls.create_prompt_model(
            MultiReviewSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.output_text_desc
                ),
            },
            name="MultiReviewOutput",
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: MultiReviewPrompt) -> type[Query]:
        """Get concrete query class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        source_cls = cls.get_source_cls(prompt)
        guide_cls = cls.get_guide_cls(prompt)
        return cls.create_prompt_model(
            MultiReviewQuery,
            prompt,
            {
                "sources": PromptModelField(
                    alias=prompt.sources,
                    annotation=list[source_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.sources_desc,
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
    def get_source_cls(cls, prompt: MultiReviewPrompt) -> type[MultiReviewSource]:
        """Get source class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            source model class
        """
        subtitle_cls = cls.get_source_subtitle_cls(prompt)
        return cls.create_prompt_model(
            MultiReviewSource,
            prompt,
            {
                "name": PromptModelField(
                    alias=prompt.source_name, description=prompt.source_name_desc
                ),
                "subtitles": PromptModelField(
                    alias=prompt.subtitles,
                    annotation=list[subtitle_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.subtitles_desc,
                ),
            },
        )

    @classmethod
    @cache
    def get_source_subtitle_cls(
        cls, prompt: MultiReviewPrompt
    ) -> type[MultiReviewSubtitle]:
        """Get source subtitle class with prompt-specific field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            source subtitle model class
        """
        return cls.create_prompt_model(
            MultiReviewSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index, description=prompt.index_desc
                ),
                "text": PromptModelField(
                    alias=prompt.text, description=prompt.source_text_desc
                ),
            },
            name="MultiReviewSourceSubtitle",
        )
