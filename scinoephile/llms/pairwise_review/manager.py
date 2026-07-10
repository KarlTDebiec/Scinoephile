#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for pairwise-review LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.llms import Answer, Manager, Query, TestCase
from scinoephile.core.llms.models import get_model_name

from .prompt import PairwiseReviewPrompt

__all__ = ["PairwiseReviewManager"]


class PairwiseReviewManager(Manager):
    """Factories for pairwise-review LLM classes."""

    operation: ClassVar[str] = "pairwise-review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[PairwiseReviewPrompt] = PairwiseReviewPrompt()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt: PairwiseReviewPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        fields: dict[str, Any] = {
            prompt.output: (
                str,
                Field("", description=prompt.output_desc, max_length=1000),
            ),
            prompt.note: (
                str,
                Field("", description=prompt.note_desc, max_length=1000),
            ),
        }
        model = create_model(
            get_model_name("PairwiseReviewAnswer", prompt.name),
            __base__=Answer,
            __module__=Answer.__module__,
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
        """Get concrete query class with provided configuration.

        Arguments:
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        fields: dict[str, Any] = {
            prompt.target: (
                str,
                Field(..., description=prompt.target_desc, max_length=1000),
            ),
            prompt.reference: (
                str,
                Field(..., description=prompt.reference_desc, max_length=1000),
            ),
        }
        model = create_model(
            get_model_name("PairwiseReviewQuery", prompt.name),
            __base__=Query,
            __module__=Query.__module__,
            **fields,
        )
        model.prompt = prompt
        return model

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on whether the target is revised.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        if model.answer is None:
            return 0
        prompt: PairwiseReviewPrompt = getattr(model, "prompt")
        target = getattr(model.query, prompt.target)
        output = getattr(model.answer, prompt.output)
        if output and output != target:
            return 1
        return 0

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure an output and its note are internally consistent.

        Unchanged full-text outputs from legacy pairwise-review data are normalized to
        the empty-string convention used by the other review operations.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        if model.answer is None:
            return model

        prompt: PairwiseReviewPrompt = getattr(model, "prompt")
        target = getattr(model.query, prompt.target)
        output = getattr(model.answer, prompt.output)
        note = getattr(model.answer, prompt.note)
        if output == target:
            setattr(model.answer, prompt.output, "")
            setattr(model.answer, prompt.note, "")
        elif output and not note:
            raise ValueError(prompt.note_missing_err)
        elif not output and note:
            raise ValueError(prompt.output_missing_err)
        return model
