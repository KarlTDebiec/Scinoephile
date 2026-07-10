#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for guided-review LLM classes."""

from __future__ import annotations

import re
from functools import cache
from typing import Any, ClassVar, cast

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import (
    Answer,
    Manager,
    Prompt,
    Query,
    TestCase,
)
from scinoephile.core.llms.models import get_model_name

from .prompt import GuidedReviewPrompt

__all__ = ["GuidedReviewManager"]


class GuidedReviewManager(Manager):
    """Factories for guided-review LLM classes."""

    operation: ClassVar[str] = "guided-review"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GuidedReviewPrompt] = GuidedReviewPrompt.from_attributes()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        target_size: int,
        guide_size: int,
        prompt: GuidedReviewPrompt = GuidedReviewPrompt.from_attributes(),
    ) -> type[Answer]:
        """Get concrete answer class with provided block sizes.

        Arguments:
            target_size: number of target subtitles
            guide_size: number of guide subtitles
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        cls._validate_sizes(target_size, guide_size)
        fields: dict[str, Any] = {}
        for idx in range(1, target_size + 1):
            fields[prompt.output(idx)] = (
                str,
                Field("", description=prompt.output_desc(idx), max_length=1000),
            )
            fields[prompt.note(idx)] = (
                str,
                Field("", description=prompt.note_desc(idx), max_length=1000),
            )
        model = create_model(
            get_model_name(
                "GuidedReviewAnswer",
                f"{target_size}_{guide_size}_{prompt.name}",
            ),
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.llm_prompt = prompt
        setattr(model, "target_size", target_size)
        setattr(model, "guide_size", guide_size)
        return model

    @classmethod
    @cache
    def get_query_cls(
        cls,
        target_size: int,
        guide_size: int,
        prompt: GuidedReviewPrompt = GuidedReviewPrompt.from_attributes(),
    ) -> type[Query]:
        """Get concrete query class with provided block sizes.

        Arguments:
            target_size: number of target subtitles
            guide_size: number of guide subtitles
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        cls._validate_sizes(target_size, guide_size)
        fields: dict[str, Any] = {}
        for idx in range(1, target_size + 1):
            fields[prompt.target(idx)] = (
                str,
                Field(..., description=prompt.target_desc(idx), max_length=1000),
            )
        for idx in range(1, guide_size + 1):
            fields[prompt.guide(idx)] = (
                str,
                Field(..., description=prompt.guide_desc(idx), max_length=1000),
            )
        model = create_model(
            get_model_name(
                "GuidedReviewQuery",
                f"{target_size}_{guide_size}_{prompt.name}",
            ),
            __base__=Query,
            __module__=Query.__module__,
            **fields,
        )
        model.llm_prompt = prompt
        setattr(model, "target_size", target_size)
        setattr(model, "guide_size", guide_size)
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        target_size: int,
        guide_size: int,
        prompt: GuidedReviewPrompt = GuidedReviewPrompt.from_attributes(),
    ) -> type[TestCase]:
        """Get concrete test case class with provided block sizes.

        Arguments:
            target_size: number of target subtitles
            guide_size: number of guide subtitles
            prompt: text for LLM correspondence
        Returns:
            test case model class
        """
        query_cls = cls.get_query_cls(target_size, guide_size, prompt)
        answer_cls = cls.get_answer_cls(target_size, guide_size, prompt)
        fields = cls.get_test_case_fields(query_cls, answer_cls, prompt)
        validators = cls.get_test_case_validators()
        model = create_model(
            get_model_name(
                "GuidedReviewTestCase",
                f"{target_size}_{guide_size}_{prompt.name}",
            ),
            __base__=TestCase,
            __module__=TestCase.__module__,
            __validators__=validators,
            **fields,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.llm_prompt = prompt
        setattr(model, "target_size", target_size)
        setattr(model, "guide_size", guide_size)
        setattr(model, "get_auto_verified", cls.get_auto_verified)
        setattr(model, "get_min_difficulty", cls.get_min_difficulty)
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict) -> type[TestCase]:
        """Get concrete test case class for canonical serialized data.

        Arguments:
            data: serialized test case data
        Returns:
            test case model class
        """
        prompt = cls.base_prompt
        target_pattern = re.compile(rf"^{re.escape(prompt.target_pfx)}\d+$")
        guide_pattern = re.compile(rf"^{re.escape(prompt.guide_pfx)}\d+$")
        target_size = sum(1 for field in data["query"] if target_pattern.match(field))
        guide_size = sum(1 for field in data["query"] if guide_pattern.match(field))
        return cls.get_test_case_cls(target_size, guide_size, prompt)

    @classmethod
    def get_test_case_cls_with_prompt(
        cls,
        test_case_cls: type[TestCase],
        prompt: Prompt,
    ) -> type[TestCase]:
        """Get an equivalently sized test-case class for another prompt.

        Arguments:
            test_case_cls: test-case class whose sizes should be preserved
            prompt: prompt whose correspondence fields should be used
        Returns:
            equivalently sized test-case class
        """
        target_size: int = getattr(test_case_cls, "target_size")
        guide_size: int = getattr(test_case_cls, "guide_size")
        return cls.get_test_case_cls(
            target_size=target_size,
            guide_size=guide_size,
            prompt=cast(GuidedReviewPrompt, prompt),
        )

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Get minimum difficulty based on whether any target is revised.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        if model.answer is None:
            return 0
        prompt: GuidedReviewPrompt = getattr(model, "llm_prompt")
        target_size: int = getattr(model, "target_size")
        for idx in range(1, target_size + 1):
            target = getattr(model.query, prompt.target(idx))
            output = getattr(model.answer, prompt.output(idx))
            if output and output != target:
                return 1
        return 0

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Ensure outputs and notes are internally consistent.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        if model.answer is None:
            return model
        prompt: GuidedReviewPrompt = getattr(model, "llm_prompt")
        target_size: int = getattr(model, "target_size")
        for idx in range(1, target_size + 1):
            target = getattr(model.query, prompt.target(idx))
            output = getattr(model.answer, prompt.output(idx))
            note = getattr(model.answer, prompt.note(idx))
            if output == target:
                setattr(model.answer, prompt.output(idx), "")
                setattr(model.answer, prompt.note(idx), "")
            elif output and not note:
                raise ValueError(prompt.note_missing_err(idx))
            elif not output and note:
                raise ValueError(prompt.output_missing_err(idx))
        return model

    @staticmethod
    def _validate_sizes(target_size: int, guide_size: int):
        """Validate dynamic model sizes.

        Arguments:
            target_size: number of target subtitles
            guide_size: number of guide subtitles
        """
        if target_size < 1:
            raise ScinoephileError("Target size must be at least 1.")
        if guide_size < 0:
            raise ScinoephileError("Guide size must not be negative.")
