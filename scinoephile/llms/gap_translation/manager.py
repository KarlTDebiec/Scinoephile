#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific gap-translation LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar, cast

from pydantic import Field, create_model

from scinoephile.core.llms import (
    Answer,
    Manager,
    Query,
    TestCase,
)
from scinoephile.core.llms.models import get_model_name

from .models import (
    GapTranslationAnswer,
    GapTranslationQuery,
    GapTranslationSubtitle,
    GapTranslationTestCase,
)
from .prompt import GapTranslationPrompt

__all__ = ["GapTranslationManager"]


class GapTranslationManager(Manager):
    """Factories for prompt-specific gap-translation LLM classes."""

    operation: ClassVar[str] = "gap-translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GapTranslationPrompt] = GapTranslationPrompt()
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
        fields: dict[str, Any] = {
            "outputs": (
                list[output_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.outputs,
                    description=prompt.outputs_desc,
                ),
            ),
        }
        model = create_model(
            get_model_name("GapTranslationAnswer", prompt.name),
            __base__=GapTranslationAnswer,
            __module__=GapTranslationAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_guide_cls(
        cls, prompt: GapTranslationPrompt
    ) -> type[GapTranslationSubtitle]:
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
                ),
            ),
        }
        return create_model(
            get_model_name("GapTranslationGuide", prompt.name),
            __base__=GapTranslationSubtitle,
            __module__=GapTranslationQuery.__module__,
            **fields,
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
            get_model_name("GapTranslationOutput", prompt.name),
            __base__=GapTranslationSubtitle,
            __module__=GapTranslationAnswer.__module__,
            **fields,
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
        fields: dict[str, Any] = {
            "targets": (
                list[target_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.targets,
                    description=prompt.targets_desc,
                ),
            ),
            "guides": (
                list[guide_cls],  # ty: ignore[invalid-type-form]
                Field(
                    ...,
                    alias=prompt.guides,
                    description=prompt.guides_desc,
                    min_length=1,
                ),
            ),
        }
        model = create_model(
            get_model_name("GapTranslationQuery", prompt.name),
            __base__=GapTranslationQuery,
            __module__=GapTranslationQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_target_cls(
        cls, prompt: GapTranslationPrompt
    ) -> type[GapTranslationSubtitle]:
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
                ),
            ),
        }
        return create_model(
            get_model_name("GapTranslationTarget", prompt.name),
            __base__=GapTranslationSubtitle,
            __module__=GapTranslationQuery.__module__,
            **fields,
        )

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure outputs exactly fill the guide indexes absent from targets.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        gap_model = cast(GapTranslationTestCase, model)
        if gap_model.answer is None:
            return model

        target_indexes = {target.index for target in gap_model.query.targets}
        expected_output_indexes = [
            guide.index
            for guide in gap_model.query.guides
            if guide.index not in target_indexes
        ]
        output_indexes = [output.index for output in gap_model.answer.outputs]
        if output_indexes != expected_output_indexes:
            prompt: GapTranslationPrompt = getattr(model, "prompt")
            raise ValueError(prompt.output_indices_mismatch_err)
        return model
