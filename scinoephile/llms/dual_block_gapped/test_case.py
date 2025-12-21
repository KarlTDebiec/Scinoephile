#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for dual block gapped test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import create_model

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import TestCase
from scinoephile.llms.base.models import get_model_name

from .answer import DualBlockGappedAnswer
from .prompt import DualBlockGappedPrompt
from .query import DualBlockGappedQuery

__all__ = ["DualBlockGappedTestCase"]


class DualBlockGappedTestCase(TestCase, ABC):
    """ABC for dual block gapped test cases."""

    answer_cls: ClassVar[type[DualBlockGappedAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[DualBlockGappedQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[DualBlockGappedPrompt]]
    """Text for LLM correspondence."""

    size: ClassVar[int]
    """Number of subtitles."""
    gaps: ClassVar[tuple[int, ...]]
    """Indexes of subtitles missing from the primary series (0-indexed)."""

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        gaps: tuple[int, ...],
        prompt_cls: type[DualBlockGappedPrompt] = DualBlockGappedPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            gaps: indexes of subtitles missing from the primary series
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        if any(gap < 0 or gap >= size for gap in gaps):
            raise ScinoephileError(
                f"Gap indices must be in range 0 to {size - 1}, got {gaps}."
            )

        name = get_model_name(
            cls.__name__,
            f"{size}_"
            f"{'-'.join(map(str, [gap + 1 for gap in gaps]))}_"
            f"{prompt_cls.__name__}",
        )
        query_cls = DualBlockGappedQuery.get_query_cls(size, gaps, prompt_cls)
        answer_cls = DualBlockGappedAnswer.get_answer_cls(size, gaps, prompt_cls)
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        model.size = size
        model.gaps = gaps
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data from JSON
            **kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            TestCase type with appropriate configuration
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
        return cls.get_test_case_cls(size=size, gaps=gaps, **kwargs)
