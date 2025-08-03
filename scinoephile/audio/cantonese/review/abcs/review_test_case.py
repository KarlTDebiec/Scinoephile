#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Cantonese audio review test cases."""

from __future__ import annotations

from abc import ABC
from functools import cached_property

from pydantic import Field, create_model, model_validator

from scinoephile.core.abcs import Answer, Query, TestCase
from scinoephile.core.models import format_field


class ReviewTestCase[TQuery: Query, TAnswer: Answer](TestCase[TQuery, TAnswer], ABC):
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
        query_cls: type[Query] | None = None,
        answer_cls: type[Answer] | None = None,
    ) -> type[ReviewTestCase[Query, Answer]]:
        """Get test case class for review of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
            query_cls: Optional query model, if not provided it will be created
            answer_cls: Optional answer model, if not provided it will be created
        Returns:
            ReviewTestCase type with appropriate query and answer models
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        if query_cls is None:
            query_cls = cls.get_query_cls(size)
        if answer_cls is None:
            answer_cls = cls.get_answer_cls(size)
        return create_model(
            f"ReviewTestCase_{size}",
            __base__=(
                query_cls,
                answer_cls,
                ReviewTestCase[query_cls, answer_cls],
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

    @model_validator(mode="after")
    def validate_test_case(self) -> ReviewTestCase:
        """Ensure query and answer are consistent with one another."""
        for idx in range(1, self.size + 1):
            yuewen_revised = getattr(self, f"yuewen_revised_{idx}")
            yuewen = getattr(self, f"yuewen_{idx}")
            note = getattr(self, f"note_{idx}")
            if yuewen_revised != "":
                if yuewen_revised == yuewen:
                    raise ValueError(
                        f"Answer's revised 粤文 text {idx} is not modified relative "
                        f"to query's 粤文 text {idx}, if no revision is needed an "
                        f"empty string must be provided."
                    )
                if note == "":
                    raise ValueError(
                        f"Answer's 粤文 text {idx} is modified relative to query's "
                        f"粤文 text {idx}, but no note is provided, if revision is "
                        f"needed a note must be provided."
                    )
            elif note != "":
                raise ValueError(
                    f"Answer's 粤文 text {idx} is not modified relative to query's "
                    f"粤文 text {idx}, but a note is provided, if no revisions are "
                    f"needed an empty string must be provided."
                )
        return self
