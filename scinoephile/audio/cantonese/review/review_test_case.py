#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 review test cases."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from pydantic import create_model, model_validator

from scinoephile.audio.cantonese.review.review_answer import ReviewAnswer
from scinoephile.audio.cantonese.review.review_query import ReviewQuery
from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field


class ReviewTestCase[TQuery: ReviewQuery, TAnswer: ReviewAnswer](
    TestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for 粤文 review test cases."""

    query_cls: ClassVar[type[ReviewQuery]]
    answer_cls: ClassVar[type[ReviewAnswer]]

    @property
    def size(self) -> int:
        """Get size of the test case."""
        zw_idxs = [
            int(s.split("_")[1]) - 1
            for s in self.query_fields
            if s.startswith("zhongwen_")
        ]
        return max(zw_idxs) + 1

    @property
    def source_str(self) -> str:
        """Get Python source-like string representation."""
        lines = [f"{ReviewTestCase.__name__}.get_test_case_cls({self.size})("]
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
    def get_test_case_cls(
        cls,
        size: int,
    ) -> type[ReviewTestCase[ReviewQuery, ReviewAnswer]]:
        """Get test case class for review of Cantonese audio.

        Arguments:
            size: Number of 中文 subtitles
        Returns:
            ReviewTestCase type with appropriate query and answer models
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        query_cls = ReviewQuery.get_query_cls(size)
        answer_cls = ReviewAnswer.get_answer_cls(size)
        model = create_model(
            f"{cls.__name__}_{size}",
            __base__=(query_cls, answer_cls, ReviewTestCase[query_cls, answer_cls]),
            __module__=cls.__module__,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls

        return model

    @model_validator(mode="after")
    def validate_test_case(self) -> ReviewTestCase:
        """Ensure query and answer are consistent with one another."""
        for idx in range(1, self.size + 1):
            yuewen = getattr(self, f"yuewen_{idx}")
            yuewen_revised = getattr(self, f"yuewen_revised_{idx}")
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
