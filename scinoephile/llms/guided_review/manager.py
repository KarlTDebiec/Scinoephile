#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific guided-review LLM classes."""

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

from .models import GuidedReviewAnswer, GuidedReviewQuery, GuidedReviewTestCase
from .prompt import GuidedReviewPrompt

__all__ = ["GuidedReviewManager"]


class GuidedReviewManager(Manager):
    """Factories for prompt-specific guided-review LLM classes."""

    operation: ClassVar[str] = "guided-review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GuidedReviewPrompt] = GuidedReviewTestCase.prompt
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = GuidedReviewTestCase
    """Static test-case model defining guided review's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: GuidedReviewPrompt) -> type[Answer]:
        """Get concrete answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        revision_cls = cls.get_revision_cls(prompt)
        return cls.create_prompt_model(
            GuidedReviewAnswer,
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
    def get_guide_cls(cls, prompt: GuidedReviewPrompt) -> type[TestCaseSubtitle]:
        """Get guide class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            guide model class
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
                    description=prompt.guide_text_desc,
                ),
            },
            module=GuidedReviewQuery.__module__,
            name="GuidedReviewGuide",
        )

    @classmethod
    @cache
    def get_query_cls(cls, prompt: GuidedReviewPrompt) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        target_cls = cls.get_target_cls(prompt)
        guide_cls = cls.get_guide_cls(prompt)
        return cls.create_prompt_model(
            GuidedReviewQuery,
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
    def get_revision_cls(
        cls,
        prompt: GuidedReviewPrompt,
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
            module=GuidedReviewAnswer.__module__,
            name="GuidedReviewRevision",
        )

    @classmethod
    @cache
    def get_target_cls(cls, prompt: GuidedReviewPrompt) -> type[TestCaseSubtitle]:
        """Get target class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            target model class
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
                    description=prompt.target_text_desc,
                ),
            },
            module=GuidedReviewQuery.__module__,
            name="GuidedReviewTarget",
        )
