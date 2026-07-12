#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for prompt-specific pairwise-review LLM classes."""

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

from .models import PairwiseReviewAnswer, PairwiseReviewQuery, PairwiseReviewTestCase
from .prompt import PairwiseReviewPrompt

__all__ = ["PairwiseReviewManager"]


class PairwiseReviewManager(Manager):
    """Factories for prompt-specific pairwise-review LLM classes."""

    operation: ClassVar[str] = "pairwise-review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[PairwiseReviewPrompt] = PairwiseReviewTestCase.prompt
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
        return cls.create_prompt_model(
            PairwiseReviewAnswer,
            prompt,
            {
                "output": PromptModelField(
                    alias=prompt.output,
                    description=prompt.output_desc,
                ),
                "note": PromptModelField(
                    alias=prompt.note,
                    description=prompt.note_desc,
                ),
            },
        )

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
        return cls.create_prompt_model(
            PairwiseReviewQuery,
            prompt,
            {
                "target": PromptModelField(
                    alias=prompt.target,
                    description=prompt.target_desc,
                ),
                "reference": PromptModelField(
                    alias=prompt.reference,
                    description=prompt.reference_desc,
                ),
            },
        )
