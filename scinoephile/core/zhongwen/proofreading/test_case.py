#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading test cases."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import create_model, model_validator

from scinoephile.core.abcs import Answer, Prompt, Query, TestCase
from scinoephile.core.models import format_field

from .answer import ZhongwenProofreadingAnswer
from .prompts import (
    ZhongwenProofreadingPrompt,
    ZhongwenProofreadingSimplifiedPrompt,
)
from .query import ZhongwenProofreadingQuery

__all__ = ["ZhongwenProofreadingTestCase"]


class ZhongwenProofreadingTestCase(
    TestCase[ZhongwenProofreadingQuery, ZhongwenProofreadingAnswer], ABC
):
    """Abstract base class for 中文 proofreading test cases."""

    answer_cls: ClassVar[type[Answer]]
    """Answer class for this test case."""
    query_cls: ClassVar[type[Query]]
    """Query class for this test case."""
    prompt_text: ClassVar[type[ZhongwenProofreadingPrompt]] = (
        ZhongwenProofreadingSimplifiedPrompt
    )
    """Text strings specialized for 中文 proofreading."""
    text: ClassVar[type[Prompt]] = prompt_text
    """Text strings to be used for corresponding with LLM."""

    @property
    def size(self) -> int:
        """Size of the test case."""
        idxs = [
            int(s.split("_")[1]) - 1 for s in self.query_fields if s.startswith("zimu_")
        ]
        return max(idxs) + 1

    @property
    def source_str(self) -> str:
        """Get Python source string."""
        lines = [
            f"{ZhongwenProofreadingTestCase.__name__}.get_test_case_cls({self.size}, "
            f"{self.text.__name__})("
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
        if any(getattr(self, f"xiugai_{idx}") != "" for idx in range(1, self.size + 1)):
            min_difficulty = max(min_difficulty, 1)
        return min_difficulty

    @model_validator(mode="after")
    def validate_test_case(self) -> Self:
        """Ensure query and answer together are valid."""
        for idx in range(self.size):
            zimu = getattr(self, f"zimu_{idx + 1}")
            xiugai = getattr(self, f"xiugai_{idx + 1}")
            beizhu = getattr(self, f"beizhu_{idx + 1}")
            if xiugai != "":
                if zimu == xiugai:
                    raise ValueError(
                        self.prompt_text.zimu_xiugai_equal_error.format(idx=idx + 1)
                    )
                if beizhu == "":
                    raise ValueError(
                        self.prompt_text.beizhu_missing_error.format(idx=idx + 1)
                    )
            elif beizhu != "":
                raise ValueError(
                    self.prompt_text.xiugai_missing_error.format(idx=idx + 1)
                )
        return self

    @classmethod
    @cache
    def get_test_case_cls(
        cls,
        size: int,
        text: type[ZhongwenProofreadingPrompt] = ZhongwenProofreadingSimplifiedPrompt,
    ) -> type[Self]:
        """Get concrete test case class with provided size and text.

        Arguments:
            size: number of subtitles
            text: Prompt providing descriptions and messages
        Returns:
            TestCase type with appropriate fields and text
        """
        query_cls = ZhongwenProofreadingQuery.get_query_cls(size, text=text)
        answer_cls = ZhongwenProofreadingAnswer.get_answer_cls(size, text=text)
        return create_model(
            f"{cls.__name__}_{size}_{text.__name__}",
            __base__=(query_cls, answer_cls, cls),
            __module__=cls.__module__,
            query_cls=(ClassVar[type[ZhongwenProofreadingQuery]], query_cls),
            answer_cls=(ClassVar[type[ZhongwenProofreadingAnswer]], answer_cls),
            prompt_text=(ClassVar[type[ZhongwenProofreadingPrompt]], text),
            text=(ClassVar[type[Prompt]], text),
        )
