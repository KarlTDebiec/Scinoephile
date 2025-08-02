#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Cantonese audio review test cases."""

from __future__ import annotations

from abc import ABC
from functools import cached_property

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Answer, DynamicTestCase, Query
from scinoephile.core.models import format_field


class ReviewTestCase[TQuery: Query, TAnswer: Answer](
    DynamicTestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for Cantonese audio review test cases."""

    @cached_property
    def size(self) -> int:
        """Get size of the test case."""
        zw_idxs = [
            int(s.split("_")[1]) - 1
            for s in self.query_fields
            if s.startswith("zhongwen_")
        ]
        return max(zw_idxs) + 1

    @cached_property
    def source_str(self) -> str:
        """Get Python source-like string representation."""
        if self.subclass_creation_function is None:
            raise ScinoephileError(
                "Preparation of source string for this class requires "
                "subclass_creation_function to be set at the time of creation."
            )
        lines = (
            [f"{ReviewTestCase.__name__}.get_test_case_cls({self.size})("]
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
        query_model: type[Query] | None = None,
        answer_model: type[Answer] | None = None,
    ) -> type[ReviewTestCase[Query, Answer]]:
        """Get test case class for translation of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
            query_model: Optional query model, if not provided it will be created
            answer_model: Optional answer model, if not provided it will be created
        Returns:
            TranslateTestCase type with appropriate query and answer models
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        if query_model is None:
            query_model = cls.get_query_cls(size)
        if answer_model is None:
            answer_model = cls.get_answer_cls(size)
        return create_model(
            f"ReviewTestCase_{size}",
            __base__=(
                query_model,
                answer_model,
                ReviewTestCase[query_model, answer_model],
            ),
        )

    @staticmethod
    def get_answer_cls(size: int) -> type[Answer]:
        """Get answer class for review of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
        Returns:
            Answer type with appropriate fields
        """
        answer_fields = {}
        for zw_idx in range(size):
            answer_fields[f"yuewen_revised_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Revised 粤文 text {zw_idx + 1}"),
            )
            answer_fields[f"note_{zw_idx + 1}"] = (
                str,
                Field(
                    "",
                    description=f"Note concerning revision of {zw_idx + 1}",
                    max_length=1000,
                ),
            )
        return create_model(f"ReviewAnswer_{size}", __base__=Answer, **answer_fields)

    @staticmethod
    def get_query_cls(size: int) -> type[Query]:
        """Get query class for review of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
        Returns:
            Query type with appropriate fields
        """
        query_fields = {}
        for zw_idx in range(size):
            query_fields[f"zhongwen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"中文 of text {zw_idx + 1}"),
            )
            query_fields[f"yuewen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"粤文 text {zw_idx + 1}"),
            )
        return create_model(f"ReviewQuery_{size}", __base__=Query, **query_fields)
