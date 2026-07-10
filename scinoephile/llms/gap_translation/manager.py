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

    prompt_cls: ClassVar[type[GapTranslationPrompt]] = GapTranslationPrompt
    """Base prompt class defining persisted test-case field names."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[GapTranslationPrompt] = GapTranslationPrompt,
    ) -> type[Query]:
        """Get concrete query class with provided configuration.

        Arguments:
            size: number of subtitles in the secondary block
            gaps: indices missing from the primary block
            prompt_cls: text for LLM correspondence
        Returns:
            query model class
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            "GapTranslationQuery",
            f"{size}_"
            f"{'-'.join(map(str, [gap + 1 for gap in gaps]))}_"
            f"{prompt_cls.__name__}",
        )
        fields: dict[str, Any] = {}
        for idx in range(size):
            if idx not in gaps:
                key = prompt_cls.src_1(idx + 1)
                description = prompt_cls.src_1_desc(idx + 1)
                fields[key] = (str, Field(..., description=description))
            key = prompt_cls.src_2(idx + 1)
            description = prompt_cls.src_2_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(
            name,
            __base__=Query,
            __module__=Query.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        setattr(model, "size", size)
        setattr(model, "gaps", gaps)
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[GapTranslationPrompt] = GapTranslationPrompt,
    ) -> type[Answer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles in the secondary block
            gaps: indices missing from the primary block
            prompt_cls: text for LLM correspondence
        Returns:
            answer model class
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            "GapTranslationAnswer",
            f"{size}_"
            f"{'-'.join(map(str, [gap + 1 for gap in gaps]))}_"
            f"{prompt_cls.__name__}",
        )
        fields: dict[str, Any] = {}
        for idx in gaps:
            key = prompt_cls.output(idx + 1)
            description = prompt_cls.output_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        setattr(model, "size", size)
        setattr(model, "gaps", gaps)
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[GapTranslationPrompt] = GapTranslationPrompt,
    ) -> type[TestCase]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles in the secondary block
            gaps: indices missing from the primary block
            prompt_cls: text for LLM correspondence
        Returns:
            test case model class
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            "GapTranslationTestCase",
            f"{size}_"
            f"{'-'.join(map(str, [gap + 1 for gap in gaps]))}_"
            f"{prompt_cls.__name__}",
        )
        query_cls = cls.get_query_cls(size, gaps, prompt_cls)
        answer_cls = cls.get_answer_cls(size, gaps, prompt_cls)
        fields = cls.get_test_case_fields(query_cls, answer_cls, prompt_cls)
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
        model.prompt_cls = prompt_cls
        setattr(model, "size", size)
        setattr(model, "gaps", gaps)
        setattr(model, "get_auto_verified", cls.get_auto_verified)
        setattr(model, "get_min_difficulty", cls.get_min_difficulty)
        return model

    @classmethod
    def get_test_case_cls_from_data(
        cls,
        data: dict,
        prompt_cls: type[Prompt],
    ) -> type[TestCase]:
        """Get concrete test case class for provided data.

        Arguments:
            data: data from JSON
            prompt_cls: text for LLM correspondence
        Returns:
            test case model class
        """
        prompt_cls = cast(type[GapTranslationPrompt], prompt_cls)
        size = sum(1 for key in data["query"] if key.startswith(prompt_cls.src_2_pfx))
        source_one_idxs = [
            int(key.removeprefix(prompt_cls.src_1_pfx)) - 1
            for key in data["query"]
            if key.startswith(prompt_cls.src_1_pfx)
        ]
        gaps = tuple(idx for idx in range(size) if idx not in source_one_idxs)
        return cls.get_test_case_cls(size=size, gaps=gaps, prompt_cls=prompt_cls)

    @classmethod
    def get_test_case_cls_with_prompt(
        cls,
        test_case_cls: type[TestCase],
        prompt_cls: type[Prompt],
    ) -> type[TestCase]:
        """Get a test-case class with the same size and gaps for another prompt.

        Arguments:
            test_case_cls: test-case class whose size and gaps should be preserved
            prompt_cls: prompt class whose correspondence fields should be used
        Returns:
            equivalently shaped test-case class
        """
        size: int = getattr(test_case_cls, "size")
        gaps: tuple[int, ...] = getattr(test_case_cls, "gaps")
        return cls.get_test_case_cls(
            size=size,
            gaps=gaps,
            prompt_cls=cast(type[GapTranslationPrompt], prompt_cls),
        )
