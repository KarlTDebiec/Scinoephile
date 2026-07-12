#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific guided-review LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import (
    AnnotatedTestCaseSubtitle,
    Answer,
    Manager,
    Query,
    TestCase,
    TestCaseSubtitle,
)
from scinoephile.core.llms.models import get_model_name

from .models import (
    GuidedReviewAnswer,
    GuidedReviewQuery,
    GuidedReviewTestCase,
)
from .prompt import GuidedReviewPrompt

__all__ = ["GuidedReviewManager"]


class GuidedReviewManager(Manager):
    """Factories for prompt-specific guided-review LLM classes."""

    operation: ClassVar[str] = "guided-review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GuidedReviewPrompt] = GuidedReviewPrompt()
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
        fields: dict[str, Any] = {
            "revisions": (
                list[revision_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.revisions,
                    description=prompt.revisions_desc,
                ),
            ),
        }
        model = create_model(
            get_model_name("GuidedReviewAnswer", prompt.name),
            __base__=GuidedReviewAnswer,
            __module__=GuidedReviewAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_guide_cls(cls, prompt: GuidedReviewPrompt) -> type[TestCaseSubtitle]:
        """Get guide class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            guide model class
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
                    max_length=1000,
                ),
            ),
        }
        return create_model(
            get_model_name("GuidedReviewGuide", prompt.name),
            __base__=TestCaseSubtitle,
            __module__=GuidedReviewQuery.__module__,
            **fields,
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
        fields: dict[str, Any] = {
            "targets": (
                list[target_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.targets,
                    description=prompt.targets_desc,
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
            get_model_name("GuidedReviewQuery", prompt.name),
            __base__=GuidedReviewQuery,
            __module__=GuidedReviewQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

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
                    description=prompt.revision_text_desc,
                    min_length=1,
                    max_length=1000,
                ),
            ),
            "note": (
                str,
                Field(
                    ...,
                    alias=prompt.note,
                    description=prompt.note_desc,
                    min_length=1,
                    max_length=1000,
                ),
            ),
        }
        return create_model(
            get_model_name("GuidedReviewRevision", prompt.name),
            __base__=AnnotatedTestCaseSubtitle,
            __module__=GuidedReviewAnswer.__module__,
            **fields,
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
                    description=prompt.target_text_desc,
                    max_length=1000,
                ),
            ),
        }
        return create_model(
            get_model_name("GuidedReviewTarget", prompt.name),
            __base__=TestCaseSubtitle,
            __module__=GuidedReviewQuery.__module__,
            **fields,
        )
