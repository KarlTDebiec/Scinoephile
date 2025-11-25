#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading test cases."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from pydantic import create_model, model_validator

from scinoephile.core.abcs import TestCase
from scinoephile.core.models import format_field
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_answer import (
    ZhongwenProofreadingAnswer,
)
from scinoephile.core.zhongwen.proofreading.zhongwen_proofreading_query import (
    ZhongwenProofreadingQuery,
)


class ZhongwenProofreadingTestCase[
    TQuery: ZhongwenProofreadingQuery,
    TAnswer: ZhongwenProofreadingAnswer,
](TestCase[TQuery, TAnswer], ABC):
    """Abstract base class for 中文 proofreading test cases."""

    query_cls: ClassVar[type[ZhongwenProofreadingQuery]] = ZhongwenProofreadingQuery
    answer_cls: ClassVar[type[ZhongwenProofreadingAnswer]] = ZhongwenProofreadingAnswer

    @property
    def noop(self) -> bool:
        """Whether this test case is a no-op."""
        for idx in range(1, self.size + 1):
            revised = getattr(self, f"xiugai_{idx}")
            if revised != "":
                return False
        return True

    @property
    def size(self) -> int:
        """Size of the test case."""
        idxs = [
            int(s.split("_")[1]) - 1 for s in self.query_fields if s.startswith("zimu_")
        ]
        return max(idxs) + 1

    @property
    def source_str(self) -> str:
        """Get Python source-like string representation."""
        lines = [
            f"{ZhongwenProofreadingTestCase.__name__}.get_test_case_cls({self.size})("
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
    def get_test_case_cls(
        cls,
        size: int,
    ) -> type[
        ZhongwenProofreadingTestCase[
            ZhongwenProofreadingQuery, ZhongwenProofreadingAnswer
        ]
    ]:
        """Get test case class for 中文 proofing.

        Arguments:
            size: number of subtitles
        Returns:
            ZhongwenProofreadingTestCase type with appropriate ZhongwenProofreadingQuery
            and ZhongwenProofreadingAnswer models
        Raises:
            ScinoephileError: if missing indices are out of range
        """
        query_cls = cls.query_cls.get_query_cls(size)
        answer_cls = cls.answer_cls.get_answer_cls(size)
        model = create_model(
            f"{cls.__name__}_{size}",
            __base__=(query_cls, answer_cls, cls[query_cls, answer_cls]),
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
    def validate_test_case(self) -> ZhongwenProofreadingTestCase:
        """Ensure query and answer are consistent with one another."""
        for idx in range(1, self.size + 1):
            subtitle = getattr(self, f"zimu_{idx}")
            revised = getattr(self, f"xiugai_{idx}")
            note = getattr(self, f"beizhu_{idx}")
            if revised != "":
                if revised == subtitle:
                    raise ValueError(
                        f"第 {idx} 条答案的修改文本与查询文本相同。"
                        f"如果不需要修改，应提供空字符串。"
                    )
                if note == "":
                    raise ValueError(
                        f"第 {idx} 条答案的文本已被修改，但未提供备注。"
                        f"如需修改，必须附带备注说明。"
                    )
            elif note != "":
                raise ValueError(
                    f"第 {idx} 条答案的文本未修改，但提供了备注。"
                    f"如果不需要修改，应提供空字符串。"
                )
        return self
