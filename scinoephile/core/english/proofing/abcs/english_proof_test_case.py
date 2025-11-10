#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English proof test cases."""

from __future__ import annotations

from abc import ABC
from functools import cached_property
from typing import ClassVar

from pydantic import create_model, model_validator

from scinoephile.core.abcs import TestCase
from scinoephile.core.english.proofing.abcs.english_proof_answer import (
    EnglishProofAnswer,
)
from scinoephile.core.english.proofing.abcs.english_proof_query import EnglishProofQuery
from scinoephile.core.models import format_field


class EnglishProofTestCase[TQuery: EnglishProofQuery, TAnswer: EnglishProofAnswer](
    TestCase[TQuery, TAnswer], ABC
):
    """Abstract base class for English proof test cases."""

    query_cls: ClassVar[type[EnglishProofQuery]]
    answer_cls: ClassVar[type[EnglishProofAnswer]]

    @cached_property
    def noop(self) -> bool:
        """Whether this test case is a no-op."""
        for idx in range(1, self.size + 1):
            revised = getattr(self, f"revised_{idx}")
            if revised != "":
                return False
        return True

    @cached_property
    def size(self) -> int:
        """Get size of the test case."""
        idxs = [
            int(s.split("_")[1]) - 1
            for s in self.query_fields
            if s.startswith("subtitle_")
        ]
        return max(idxs) + 1

    @cached_property
    def source_str(self) -> str:
        """Get Python source-like string representation."""
        lines = [f"{EnglishProofTestCase.__name__}.get_test_case_cls({self.size})("]
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
    ) -> type[EnglishProofTestCase[EnglishProofQuery, EnglishProofAnswer]]:
        """Get test case class for English proofing.

        Arguments:
            size: number of subtitles
        Returns:
            EnglishProofTestCase type with appropriate EnglishProofQuery and
            EnglishProofAnswer models
        Raises:
            ScinoephileError: if missing indices are out of range
        """
        query_cls = EnglishProofQuery.get_query_cls(size)
        answer_cls = EnglishProofAnswer.get_answer_cls(size)
        model = create_model(
            f"{cls.__name__}_{size}",
            __base__=(
                query_cls,
                answer_cls,
                EnglishProofTestCase[query_cls, answer_cls],
            ),
            __module__=cls.__module__,
        )
        model.query_cls = query_cls
        model.answer_cls = answer_cls

        return model

    def get_min_difficulty(self) -> int:
        """Get minimum difficulty based on the test case properties.

        0: No change needed
        1: Change needed
        2: Difficult change needed, worthy of inclusion in prompt or difficult test set
        3: Not considered realistic for LLM to handle correctly

        Returns:
            minimum difficulty level based on the test case properties
        """
        min_difficulty = super().get_min_difficulty()
        if not self.noop:
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> EnglishProofTestCase:
        """Ensure query and answer are consistent with one another."""
        for idx in range(1, self.size + 1):
            subtitle = getattr(self, f"subtitle_{idx}")
            revised = getattr(self, f"revised_{idx}")
            note = getattr(self, f"note_{idx}")
            if revised != "":
                if revised == subtitle:
                    raise ValueError(
                        f"Answer's revised text {idx} is not modified relative to "
                        f"query's text {idx}, if no revision is needed an empty string "
                        f"must be provided."
                    )
                if note == "":
                    raise ValueError(
                        f"Answer's text {idx} is modified relative to query's text "
                        f"{idx}, but no note is provided, if revision is needed a note "
                        f"must be provided."
                    )
            elif note != "":
                raise ValueError(
                    f"Answer's text {idx} is not modified relative to query's text "
                    f"{idx}, but a note is provided, if no revisions are needed an "
                    f"empty string must be provided."
                )
        return self
