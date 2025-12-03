#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription translation test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model

from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field

from .answer import TranslationAnswer
from .prompt import TranslationPrompt
from .query import TranslationQuery

__all__ = ["TranslationTestCase"]


class TranslationTestCase[TQuery: TranslationQuery, TAnswer: TranslationAnswer](
    TestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for 粤文 transcription translation test cases."""

    answer_cls: ClassVar[type[TranslationAnswer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[TranslationQuery]]
    """Query class for this test case."""
    text: ClassVar[type[TranslationPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @property
    def missing(self) -> tuple[int, ...]:
        """Indices of missing 粤文 subtitles."""
        yw_idxs = [
            int(s.split("_")[1]) - 1
            for s in self.answer_fields
            if s.startswith("yuewen_")
        ]
        return tuple(yw_idxs)

    @property
    def size(self) -> int:
        """Size of the test case."""
        zw_idxs = [
            int(s.split("_")[1]) - 1
            for s in self.query_fields
            if s.startswith("zhongwen_")
        ]
        return max(zw_idxs) + 1

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [
            f"{TranslationTestCase.__name__}.get_test_case_cls(",
            f"    {self.size}, {self.missing}, {self.text.__name__})(",
        ]
        for field in self.query_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        for field in self.answer_fields:
            value = getattr(self, field)
            if value == "":
                continue
            lines.append(format_field(field, value))
        for field in self.test_case_fields:
            value = getattr(self, field)
            lines.append(format_field(field, value))
        lines.append(")")
        return "\n".join(lines)

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        missing: tuple[int, ...],
        text: type[TranslationPrompt] = TranslationPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided size, missing, and text.

        Arguments:
            size: number of subtitles
            missing: indexes of missing subtitles
            text: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        query_cls = TranslationQuery.get_query_cls(size, missing, text)
        answer_cls = TranslationAnswer.get_answer_cls(size, missing, text)
        name = (
            f"{cls.__name__}_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}"
            f"_{text.__name__}"
        )
        return create_model(
            name[:64],
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[TranslationQuery]], query_cls),
            answer_cls=(ClassVar[type[TranslationAnswer]], answer_cls),
            text=(ClassVar[type[TranslationPrompt]], text),
        )
