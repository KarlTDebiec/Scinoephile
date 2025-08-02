#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for Cantonese audio translation tests."""

from __future__ import annotations

from abc import ABC
from functools import cached_property

from scinoephile.core.abcs import Answer, Query, TestCase
from scinoephile.core.models import format_field


class TranslateTestCase[TQuery: Query, TAnswer: Answer](TestCase[TQuery, TAnswer], ABC):
    """Abstract base class for Cantonese audio translation tests."""

    @cached_property
    def source_str(self) -> str:
        """Get Python source-like string representation."""
        query_fields = self.query_cls.model_fields
        answer_fields = self.answer_cls.model_fields

        size = max(
            [int(s.split("_")[1]) for s in query_fields if s.startswith("zhongwen_")]
        )
        missing = [
            int(s.split("_")[1]) - 1 for s in answer_fields if s.startswith("yuewen_")
        ]

        exclusions = set()
        if not self.difficulty:
            exclusions.add("difficulty")
        if not self.prompt:
            exclusions.add("prompt")
        if not self.verified:
            exclusions.add("verified")
        test_case_fields = sorted(
            list(
                set(self.model_fields)
                - set(query_fields)
                - set(answer_fields)
                - exclusions
            )
        )

        lines = (
            ["get_translate_test_case_model(", "    {size}, {missing}", ")("]
            + [format_field(field, getattr(self, field)) for field in query_fields]
            + [format_field(field, getattr(self, field)) for field in answer_fields]
            + [format_field(field, getattr(self, field)) for field in test_case_fields]
            + [")"]
        )
        return "\n".join(lines)
