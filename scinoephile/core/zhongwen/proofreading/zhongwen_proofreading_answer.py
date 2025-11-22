#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading answers."""

from __future__ import annotations

from abc import ABC
from typing import Self

from pydantic import Field, create_model

from scinoephile.core.abcs import Answer


class ZhongwenProofreadingAnswer(Answer, ABC):
    """Abstract base class for 中文 proofreading answers."""

    @classmethod
    def get_answer_cls(cls, size: int) -> type[Self]:
        """Get answer class for 中文 proofreading.

        Arguments:
            size: number of subtitles
        Returns:
            ZhongwenProofAnswer type with appropriate fields
        """
        answer_fields = {}
        for idx in range(size):
            answer_fields[f"xiugai_{idx + 1}"] = (
                str,
                Field("", description=f"第 {idx + 1} 条修改后的字幕"),
            )
            answer_fields[f"beizhu_{idx + 1}"] = (
                str,
                Field(
                    "",
                    description=f"关于第 {idx + 1} 条字幕修改的备注说明",
                    max_length=1000,
                ),
            )
        return create_model(f"{cls.__name__}_{size}", __base__=cls, **answer_fields)
