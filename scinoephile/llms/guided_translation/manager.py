#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for guided translation LLM classes."""

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

from .prompt import GuidedTranslationPrompt

__all__ = ["GuidedTranslationManager"]


class GuidedTranslationManager(Manager):
    """Factories for guided translation LLM classes."""

    operation: ClassVar[str] = "guided-translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GuidedTranslationPrompt] = (
        GuidedTranslationPrompt.from_attributes()
    )
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        source_one_size: int,
        source_two_size: int,
        prompt: GuidedTranslationPrompt = GuidedTranslationPrompt.from_attributes(),
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            source_one_size: number of subtitles in source one
            source_two_size: number of subtitles in source two
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        cls._validate_sizes(source_one_size, source_two_size)

        name = get_model_name(
            "GuidedTranslationAnswer",
            f"{source_one_size}_{source_two_size}_{prompt.name}",
        )
        fields: dict[str, Any] = {}
        for idx in range(source_one_size):
            key = prompt.output(idx + 1)
            description = prompt.output_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt = prompt
        setattr(model, "source_one_size", source_one_size)
        setattr(model, "source_two_size", source_two_size)
        return model

    @classmethod
    @cache
    def get_query_cls(
        cls,
        source_one_size: int,
        source_two_size: int,
        prompt: GuidedTranslationPrompt = GuidedTranslationPrompt.from_attributes(),
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            source_one_size: number of subtitles in source one
            source_two_size: number of subtitles in source two
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        cls._validate_sizes(source_one_size, source_two_size)

        name = get_model_name(
            "GuidedTranslationQuery",
            f"{source_one_size}_{source_two_size}_{prompt.name}",
        )
        fields: dict[str, Any] = {}
        for idx in range(source_one_size):
            key = prompt.src_1(idx + 1)
            description = prompt.src_1_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))
        for idx in range(source_two_size):
            key = prompt.src_2(idx + 1)
            description = prompt.src_2_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(
            name,
            __base__=Query,
            __module__=Query.__module__,
            **fields,
        )
        model.prompt = prompt
        setattr(model, "source_one_size", source_one_size)
        setattr(model, "source_two_size", source_two_size)
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        source_one_size: int,
        source_two_size: int,
        prompt: GuidedTranslationPrompt = GuidedTranslationPrompt.from_attributes(),
    ) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            source_one_size: number of subtitles in source one
            source_two_size: number of subtitles in source two
            prompt: text for LLM correspondence
        Returns:
            test case model class
        """
        cls._validate_sizes(source_one_size, source_two_size)

        name = get_model_name(
            "GuidedTranslationTestCase",
            f"{source_one_size}_{source_two_size}_{prompt.name}",
        )
        query_cls = cls.get_query_cls(source_one_size, source_two_size, prompt)
        answer_cls = cls.get_answer_cls(source_one_size, source_two_size, prompt)
        fields = cls.get_test_case_fields(query_cls, answer_cls, prompt)
        validators = cls.get_test_case_validators()

        model = create_model(
            name,
            __base__=TestCase,
            __module__=TestCase.__module__,
            __validators__=validators,
            **fields,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt = prompt
        setattr(model, "source_one_size", source_one_size)
        setattr(model, "source_two_size", source_two_size)
        setattr(model, "get_auto_verified", cls.get_auto_verified)
        setattr(model, "get_min_difficulty", cls.get_min_difficulty)
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict) -> type[TestCase]:
        """Get concrete test case class for canonical serialized data.

        Arguments:
            data: data from JSON
        Returns:
            test case model class
        """
        prompt = cls.base_prompt
        source_one_pattern = re.compile(rf"^{re.escape(prompt.src_1_pfx)}\d+$")
        source_two_pattern = re.compile(rf"^{re.escape(prompt.src_2_pfx)}\d+$")
        source_one_size = sum(
            1 for field in data["query"] if source_one_pattern.match(field)
        )
        source_two_size = sum(
            1 for field in data["query"] if source_two_pattern.match(field)
        )
        return cls.get_test_case_cls(
            source_one_size=source_one_size,
            source_two_size=source_two_size,
            prompt=prompt,
        )

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
        source_one_size: int = getattr(test_case_cls, "source_one_size")
        source_two_size: int = getattr(test_case_cls, "source_two_size")
        return cls.get_test_case_cls(
            source_one_size=source_one_size,
            source_two_size=source_two_size,
            prompt=cast(GuidedTranslationPrompt, prompt),
        )

    @staticmethod
    def _validate_sizes(source_one_size: int, source_two_size: int):
        """Validate dynamic model sizes.

        Arguments:
            source_one_size: number of subtitles in source one
            source_two_size: number of subtitles in source two
        """
        if source_one_size < 1:
            raise ScinoephileError("Source one size must be at least 1.")
        if source_two_size < 0:
            raise ScinoephileError("Source two size must not be negative.")
