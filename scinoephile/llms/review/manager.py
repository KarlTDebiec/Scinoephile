#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific review LLM classes."""

from __future__ import annotations

from functools import cache
from typing import ClassVar

from scinoephile.core.llms import (
    AnnotatedTestCaseSubtitle,
    Answer,
    Manager,
    PromptModelField,
    Query,
    TestCase,
    TestCaseSubtitle,
)

from .models import ReviewAnswer, ReviewQuery, ReviewTestCase
from .prompt import ReviewPrompt

__all__ = ["ReviewManager"]


class ReviewManager(Manager):
    """Factories for prompt-specific review LLM classes."""

    operation: ClassVar[str] = "review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[ReviewPrompt] = ReviewTestCase.prompt
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = ReviewTestCase
    """Static test-case model defining review's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: ReviewPrompt) -> type[Answer]:
        """Get concrete answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        revision_cls = cls.get_revision_cls(prompt)
        return cls.create_prompt_model(
            ReviewAnswer,
            prompt,
            {
                "revisions": PromptModelField(
                    alias=prompt.revisions,
                    annotation=list[revision_cls],  # ty: ignore[invalid-type-form]
                    description=prompt.revisions_desc,
                ),
            },
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: ReviewPrompt) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        subtitle_cls = cls.get_subtitle_cls(prompt)
        return cls.create_prompt_model(
            ReviewQuery,
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
    def get_revision_cls(
        cls,
        prompt: ReviewPrompt,
    ) -> type[AnnotatedTestCaseSubtitle]:
        """Get revision class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            revision model class
        """
        return cls.create_prompt_model(
            AnnotatedTestCaseSubtitle,
            prompt,
            {
                "index": PromptModelField(
                    alias=prompt.index,
                    description=prompt.index_desc,
                ),
                "text": PromptModelField(
                    alias=prompt.text,
                    description=prompt.revision_text_desc,
                ),
                "note": PromptModelField(
                    alias=prompt.note,
                    description=prompt.note_desc,
                ),
            },
            module=ReviewAnswer.__module__,
            name="ReviewRevision",
        )

    @classmethod
    @cache
    def get_subtitle_cls(cls, prompt: ReviewPrompt) -> type[TestCaseSubtitle]:
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
            module=ReviewQuery.__module__,
            name="ReviewSubtitle",
        )
