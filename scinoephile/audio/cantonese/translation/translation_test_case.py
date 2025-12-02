#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 translation test cases."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from pydantic import create_model

from scinoephile.audio.cantonese.translation.translation_answer import (
    TranslationAnswer,
)
from scinoephile.audio.cantonese.translation.translation_query import (
    TranslationQuery,
)
from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field


class TranslationTestCase[TQuery: TranslationQuery, TAnswer: TranslationAnswer](
    TestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for 粤文 translation test cases."""

    query_cls: ClassVar[type[TranslationQuery]]
    answer_cls: ClassVar[type[TranslationAnswer]]

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
        """Python source-like string representation."""
        lines = (
            [
                f"{TranslationTestCase.__name__}.get_test_case_cls(",
                f"    {self.size}, {self.missing},",
                ")(",
            ]
            + [format_field(f, getattr(self, f)) for f in self.query_fields]
            + [format_field(f, getattr(self, f)) for f in self.answer_fields]
            + [format_field(f, getattr(self, f)) for f in self.test_case_fields]
            + [")"]
        )
        return "\n".join(lines)

    @classmethod
    def get_test_case_cls(
        cls,
        size: int,
        missing: tuple[int, ...],
    ) -> type[TranslationTestCase[TranslationQuery, TranslationAnswer]]:
        """Get test case class 粤文 translation.

        Arguments:
            size: Number of 中文 subtitles
            missing: Indices of 中文 subtitles that are missing 粤文
        Returns:
            TranslateTestCase type with appropriate query and answer models
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        query_cls = TranslationQuery.get_query_cls(size, missing)
        answer_cls = TranslationAnswer.get_answer_cls(size, missing)
        name = f"{cls.__name__}_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}"
        model = create_model(
            name[:64],
            __base__=(
                query_cls,
                answer_cls,
                TranslationTestCase[query_cls, answer_cls],
            ),
            __module__=cls.__module__,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls

        return model
