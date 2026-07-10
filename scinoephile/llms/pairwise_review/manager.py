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

    prompt_cls: ClassVar[type[PairwiseReviewPrompt]] = PairwiseReviewPrompt
    """Base prompt class defining persisted test-case field names."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[PairwiseReviewPrompt] = PairwiseReviewPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        fields: dict[str, Any] = {
            prompt_cls.output: (
                str,
                Field("", description=prompt_cls.output_desc, max_length=1000),
            ),
            prompt_cls.note: (
                str,
                Field("", description=prompt_cls.note_desc, max_length=1000),
            ),
        }
        model = create_model(
            get_model_name("PairwiseReviewAnswer", prompt_cls.__name__),
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        return model

    @classmethod
    @cache
    def get_query_cls(
        cls,
        prompt_cls: type[PairwiseReviewPrompt] = PairwiseReviewPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        fields: dict[str, Any] = {
            prompt_cls.target: (
                str,
                Field(..., description=prompt_cls.target_desc, max_length=1000),
            ),
            prompt_cls.reference: (
                str,
                Field(..., description=prompt_cls.reference_desc, max_length=1000),
            ),
        }
        model = create_model(
            get_model_name("PairwiseReviewQuery", prompt_cls.__name__),
            __base__=Query,
            __module__=Query.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
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
        prompt_cls: type[PairwiseReviewPrompt] = getattr(model, "prompt_cls")
        target = getattr(model.query, prompt_cls.target)
        output = getattr(model.answer, prompt_cls.output)
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

        prompt_cls: type[PairwiseReviewPrompt] = getattr(model, "prompt_cls")
        target = getattr(model.query, prompt_cls.target)
        output = getattr(model.answer, prompt_cls.output)
        note = getattr(model.answer, prompt_cls.note)
        if output == target:
            setattr(model.answer, prompt_cls.output, "")
            setattr(model.answer, prompt_cls.note, "")
        elif output and not note:
            raise ValueError(prompt_cls.note_missing_err)
        elif not output and note:
            raise ValueError(prompt_cls.output_missing_err)
        return model
