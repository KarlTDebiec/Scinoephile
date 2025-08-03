#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Cantonese audio translation test cases."""

from __future__ import annotations

from abc import ABC
from functools import cached_property

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Answer, DynamicTestCase, Query
from scinoephile.core.models import format_field


class TranslateTestCase[TQuery: Query, TAnswer: Answer](
    DynamicTestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for Cantonese audio translation test cases."""

    @cached_property
    def missing(self) -> tuple[int, ...]:
        """Indices of missing 粤文 subtitles."""
        yw_idxs = [
            int(s.split("_")[1]) - 1
            for s in self.answer_fields
            if s.startswith("yuewen_")
        ]
        return tuple(yw_idxs)

    @cached_property
    def size(self) -> int:
        """Size of the test case."""
        zw_idxs = [
            int(s.split("_")[1]) - 1
            for s in self.query_fields
            if s.startswith("zhongwen_")
        ]
        return max(zw_idxs) + 1

    @cached_property
    def source_str(self) -> str:
        """Python source-like string representation."""
        lines = (
            [
                f"{TranslateTestCase.__name__}.get_test_case_cls(",
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
        query_cls: type[Query] | None = None,
        answer_cls: type[Answer] | None = None,
    ) -> type[TranslateTestCase[Query, Answer]]:
        """Get test case class for translation of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
            missing: Indices of 中文 subtitles that are missing 粤文
            query_cls: Optional query class, if not provided it will be created
            answer_cls: Optional answer class, if not provided it will be created
        Returns:
            TranslateTestCase type with appropriate query and answer models
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        if query_cls is None:
            query_cls = cls.get_query_cls(size, missing)
        if answer_cls is None:
            answer_cls = cls.get_answer_cls(size, missing)
        return create_model(
            f"TranslateTestCase_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}",
            __base__=(
                query_cls,
                answer_cls,
                TranslateTestCase[query_cls, answer_cls],
            ),
        )

    @staticmethod
    def get_answer_cls(size: int, missing: tuple[int, ...]) -> type[Answer]:
        """Get answer class for translation of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
            missing: Indices of 中文 subtitles that are missing 粤文
        Returns:
            Answer type with appropriate fields
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )
        answer_fields = {}
        for zw_idx in range(size):
            if zw_idx in missing:
                answer_fields[f"yuewen_{zw_idx + 1}"] = (
                    str,
                    Field(..., description=f"Translated 粤文 text {zw_idx + 1}"),
                )
        return create_model(
            f"TranslateAnswer_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}",
            __base__=Answer,
            **answer_fields,
        )

    @staticmethod
    def get_query_cls(size: int, missing: tuple[int, ...]) -> type[Query]:
        """Get query class for translation of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
            missing: Indices of 中文 subtitles that are missing 粤文
        Returns:
            Query type with appropriate fields
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )
        query_fields = {}
        for zw_idx in range(size):
            query_fields[f"zhongwen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Known 中文 text {zw_idx + 1}"),
            )
            if zw_idx not in missing:
                query_fields[f"yuewen_{zw_idx + 1}"] = (
                    str,
                    Field(..., description=f"Known 粤文 text {zw_idx + 1}"),
                )
        return create_model(
            f"TranslateQuery_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}",
            __base__=Query,
            **query_fields,
        )
