#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for translation of 粤文 from 中文 test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar, Self

from pydantic import create_model

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import TestCase
from scinoephile.llms.base.models import get_model_name

from .answer import YueFromZhoTranslationAnswer
from .prompts import YueHansFromZhoTranslationPrompt
from .query import YueFromZhoTranslationQuery

__all__ = ["YueFromZhoTranslationTestCase"]


class YueFromZhoTranslationTestCase(TestCase, ABC):
    """ABC for translation of 粤文 from 中文 test cases."""

    answer_cls: ClassVar[type[YueFromZhoTranslationAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[YueFromZhoTranslationQuery]]
    """Query class for this test case."""
    prompt_cls: ClassVar[type[YueHansFromZhoTranslationPrompt]]
    """Text for LLM correspondence."""

    size: ClassVar[int]
    """Number of subtitles."""
    missing: ClassVar[tuple[int, ...]]
    """Indexes of missing subtitles (0-indexed)."""

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        missing: tuple[int, ...],
        prompt_cls: type[
            YueHansFromZhoTranslationPrompt
        ] = YueHansFromZhoTranslationPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided configuration.

        Arguments:
            size: number of subtitles
            missing: indexes of missing subtitles
            prompt_cls: text for LLM correspondence
        Returns:
            TestCase type with appropriate configuration
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )

        name = get_model_name(
            cls.__name__,
            f"{size}_"
            f"{'-'.join(map(str, [m + 1 for m in missing]))}_"
            f"{prompt_cls.__name__}",
        )
        query_cls = YueFromZhoTranslationQuery.get_query_cls(size, missing, prompt_cls)
        answer_cls = YueFromZhoTranslationAnswer.get_answer_cls(
            size, missing, prompt_cls
        )
        fields = cls.get_fields(query_cls, answer_cls, prompt_cls)

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.query_cls = query_cls
        model.answer_cls = answer_cls
        model.prompt_cls = prompt_cls
        model.size = size
        model.missing = missing
        return model

    @classmethod
    def get_test_case_cls_from_data(cls, data: dict, **kwargs: Any) -> type[Self]:
        """Get concrete test case class for provided data with provided configuration.

        Arguments:
            data: data from JSON
            kwargs: additional keyword arguments passed to get_test_case_cls
        Returns:
            TestCase type with appropriate configuration
        """
        if (prompt_cls := kwargs.get("prompt_cls")) is None:
            raise ScinoephileError("prompt_cls must be provided as a keyword argument")
        size = sum(
            1 for key in data["query"] if key.startswith(prompt_cls.source_two_pfx)
        )
        source_one_idxs = [
            int(key.removeprefix(prompt_cls.source_one_pfx)) - 1
            for key in data["query"]
            if key.startswith(prompt_cls.source_one_pfx)
        ]
        missing = tuple(idx for idx in range(size) if idx not in source_one_idxs)
        return cls.get_test_case_cls(size=size, missing=missing, **kwargs)
