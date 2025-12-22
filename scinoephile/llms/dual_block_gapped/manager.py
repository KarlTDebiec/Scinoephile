#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factories for dual block / subtitle block (gapped) LLM classes."""

from __future__ import annotations

from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import Answer, Manager, Query, TestCase
from scinoephile.llms.base.models import get_model_name

from .prompt import DualBlockGappedPrompt

__all__ = ["DualBlockGappedManager"]


class DualBlockGappedManager(Manager):
    """Factories for dual block / subtitle block (gapped) LLM classes."""

    prompt_cls: ClassVar[type[DualBlockGappedPrompt]] = DualBlockGappedPrompt
    """Default prompt class."""

    @classmethod
    @cache
    def get_query_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[DualBlockGappedPrompt] = DualBlockGappedPrompt,
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
            "DualBlockGappedQuery",
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
        model.size = size
        model.gaps = gaps
        return model

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[DualBlockGappedPrompt] = DualBlockGappedPrompt,
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
            "DualBlockGappedAnswer",
            f"{size}_"
            f"{'-'.join(map(str, [gap + 1 for gap in gaps]))}_"
            f"{prompt_cls.__name__}",
        )
        fields: dict[str, Any] = {}
        for idx in gaps:
            key = prompt_cls.src_1(idx + 1)
            description = prompt_cls.src_1_desc(idx + 1)
            fields[key] = (str, Field(..., description=description))

        model = create_model(
            name,
            __base__=Answer,
            __module__=Answer.__module__,
            **fields,
        )
        model.prompt_cls = prompt_cls
        model.size = size
        model.gaps = gaps
        return model

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[DualBlockGappedPrompt] = DualBlockGappedPrompt,
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
            "DualBlockGappedTestCase",
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
        model.size = size
        model.gaps = gaps
        model.get_auto_verified = cls.get_auto_verified  # type: ignore[assignment]
        model.get_min_difficulty = cls.get_min_difficulty  # type: ignore[assignment]
        return model  # ty:ignore[invalid-return-type]

    @classmethod
    def get_test_case_cls_from_data(
        cls,
        data: dict,
        **kwargs: Any,
    ) -> type[TestCase]:
        """Get concrete test case class for provided data.

        Arguments:
            data: data from JSON
            **kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            test case model class
        """
        if (prompt_cls := kwargs.get("prompt_cls")) is None:
            raise ScinoephileError("prompt_cls must be provided as a keyword argument")
        size = sum(1 for key in data["query"] if key.startswith(prompt_cls.src_2_pfx))
        source_one_idxs = [
            int(key.removeprefix(prompt_cls.src_1_pfx)) - 1
            for key in data["query"]
            if key.startswith(prompt_cls.src_1_pfx)
        ]
        gaps = tuple(idx for idx in range(size) if idx not in source_one_idxs)
        return cls.get_test_case_cls(size=size, gaps=gaps, prompt_cls=prompt_cls)
