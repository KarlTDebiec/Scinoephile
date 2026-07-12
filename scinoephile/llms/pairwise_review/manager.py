#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific pairwise-review LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .models import (
    PairwiseReviewAnswer,
    PairwiseReviewQuery,
    PairwiseReviewTestCase,
)
from .prompt import PairwiseReviewPrompt

__all__ = ["PairwiseReviewManager"]


class PairwiseReviewManager(Manager):
    """Factories for prompt-specific pairwise-review LLM classes."""

    operation: ClassVar[str] = "pairwise-review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[PairwiseReviewPrompt] = PairwiseReviewPrompt()
    """Base prompt defining persisted test-case field names."""
    test_case_base_cls: ClassVar[type[TestCase]] = PairwiseReviewTestCase
    """Static test-case model defining pairwise review's semantic shape."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt: PairwiseReviewPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            answer model class
        """
        fields: dict[str, Any] = {
            "output": (
                str,
                Field(
                    "",
                    alias=prompt.output,
                    description=prompt.output_desc,
                    max_length=1000,
                ),
            ),
            "note": (
                str,
                Field(
                    "",
                    alias=prompt.note,
                    description=prompt.note_desc,
                    max_length=1000,
                ),
            ),
        }
        model = create_model(
            get_model_name("PairwiseReviewAnswer", prompt.name),
            __base__=PairwiseReviewAnswer,
            __module__=PairwiseReviewAnswer.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt: PairwiseReviewPrompt,
    ) -> type[Query]:
        """Get concrete query class with prompt-specific JSON field aliases.

        Arguments:
            prompt: text and field aliases for LLM correspondence
        Returns:
            query model class
        """
        fields: dict[str, Any] = {
            "target": (
                str,
                Field(
                    ...,
                    alias=prompt.target,
                    description=prompt.target_desc,
                    max_length=1000,
                ),
            ),
            "reference": (
                str,
                Field(
                    ...,
                    alias=prompt.reference,
                    description=prompt.reference_desc,
                    max_length=1000,
                ),
            ),
        }
        model = create_model(
            get_model_name("PairwiseReviewQuery", prompt.name),
            __base__=PairwiseReviewQuery,
            __module__=PairwiseReviewQuery.__module__,
            **fields,
        )
        model.prompt = prompt
        return model
