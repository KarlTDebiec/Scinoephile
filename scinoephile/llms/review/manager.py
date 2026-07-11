#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific review LLM classes."""

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
    ReviewAnswer,
    ReviewQuery,
    ReviewTestCase,
)
from .prompt import ReviewPrompt

__all__ = ["ReviewManager"]


class ReviewManager(Manager):
    """Factories for prompt-specific review LLM classes."""

    operation: ClassVar[str] = "review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[ReviewPrompt] = ReviewPrompt()
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
            get_model_name("ReviewAnswer", prompt.name),
            __base__=ReviewAnswer,
            __module__=ReviewAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

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
            get_model_name("ReviewQuery", prompt.name),
            __base__=ReviewQuery,
            __module__=ReviewQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

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
            get_model_name("ReviewRevision", prompt.name),
            __base__=AnnotatedTestCaseSubtitle,
            __module__=ReviewAnswer.__module__,
            **fields,
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
            get_model_name("ReviewSubtitle", prompt.name),
            __base__=TestCaseSubtitle,
            __module__=ReviewQuery.__module__,
            **fields,
        )
