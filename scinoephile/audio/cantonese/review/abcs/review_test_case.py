#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 review test cases."""

from __future__ import annotations

from abc import ABC
from functools import cached_property

from pydantic import create_model, model_validator

from scinoephile.audio.cantonese.review.abcs.review_answer import ReviewAnswer
from scinoephile.audio.cantonese.review.abcs.review_query import ReviewQuery
from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field


class ReviewTestCase[TQuery: ReviewQuery, TAnswer: ReviewAnswer](
    TestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for 粤文 review test cases."""

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
        query_cls: type[ReviewQuery] | None = None,
        answer_cls: type[ReviewAnswer] | None = None,
    ) -> type[ReviewTestCase[ReviewQuery, ReviewAnswer]]:
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
            query_cls = ReviewQuery.get_query_cls(size)
        if answer_cls is None:
            answer_cls = ReviewAnswer.get_answer_cls(size)
        return create_model(
            f"ReviewTestCase_{size}",
            __base__=(
                query_cls,
                answer_cls,
                ReviewTestCase[query_cls, answer_cls],
            ),
        )

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
