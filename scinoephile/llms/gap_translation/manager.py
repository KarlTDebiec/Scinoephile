#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for gap translation LLM classes."""

from __future__ import annotations

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

from .prompt import GapTranslationPrompt

__all__ = ["GapTranslationManager"]


class GapTranslationManager(Manager):
    """Factories for gap translation LLM classes."""

    operation: ClassVar[str] = "gap-translation"
    """Stable operation identifier used in persistence and CLIs."""
    base_prompt: ClassVar[GapTranslationPrompt] = GapTranslationPrompt()
    """Base prompt defining persisted test-case field names."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt: GapTranslationPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles in the secondary block
            gaps: indices missing from the primary block
            prompt: text for LLM correspondence
        Returns:
            query model class
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            "GapTranslationQuery",
            f"{size}_{'-'.join(map(str, [gap + 1 for gap in gaps]))}_{prompt.name}",
        )
        fields: dict[str, Any] = {}
        for idx in range(size):
            if idx not in gaps:
                key = prompt.src_1(idx + 1)
                description = prompt.src_1_desc(idx + 1)
                fields[key] = (str, Field(..., description=description))
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
        setattr(model, "size", size)
        setattr(model, "gaps", gaps)
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt: GapTranslationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles in the secondary block
            gaps: indices missing from the primary block
            prompt: text for LLM correspondence
        Returns:
            answer model class
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            "GapTranslationAnswer",
            f"{size}_{'-'.join(map(str, [gap + 1 for gap in gaps]))}_{prompt.name}",
        )
        fields: dict[str, Any] = {}
        for idx in gaps:
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
        setattr(model, "size", size)
        setattr(model, "gaps", gaps)
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt: GapTranslationPrompt,
    ) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles in the secondary block
            gaps: indices missing from the primary block
            prompt: text for LLM correspondence
        Returns:
            test case model class
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            "GapTranslationTestCase",
            f"{size}_{'-'.join(map(str, [gap + 1 for gap in gaps]))}_{prompt.name}",
        )
        query_cls = cls.get_query_cls(size, gaps, prompt)
        answer_cls = cls.get_answer_cls(size, gaps, prompt)
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
        setattr(model, "size", size)
        setattr(model, "gaps", gaps)
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
        size = sum(1 for key in data["query"] if key.startswith(prompt.src_2_pfx))
        source_one_idxs = [
            int(key.removeprefix(prompt.src_1_pfx)) - 1
            for key in data["query"]
            if key.startswith(prompt.src_1_pfx)
        ]
        gaps = tuple(idx for idx in range(size) if idx not in source_one_idxs)
        return cls.get_test_case_cls(size=size, gaps=gaps, prompt=prompt)

    @classmethod
    def get_test_case_cls_with_prompt(
        cls,
        test_case_cls: type[TestCase],
        prompt: Prompt,
    ) -> type[TestCase]:
        """Get a test-case class with the same size and gaps for another prompt.

        Arguments:
            test_case_cls: test-case class whose size and gaps should be preserved
            prompt: prompt whose correspondence fields should be used
        Returns:
            equivalently shaped test-case class
        """
        size: int = getattr(test_case_cls, "size")
        gaps: tuple[int, ...] = getattr(test_case_cls, "gaps")
        return cls.get_test_case_cls(
            size=size,
            gaps=gaps,
            prompt=cast(GapTranslationPrompt, prompt),
        )
