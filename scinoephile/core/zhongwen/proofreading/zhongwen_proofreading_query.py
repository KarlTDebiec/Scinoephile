#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 中文 proofreading queries."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Self

from pydantic import Field, create_model

from scinoephile.core.abcs import Query


class ZhongwenProofreadingQuery(Query, ABC):
    """Abstract base class for 中文 proofreading queries."""

    @classmethod
    @cache
    def get_query_cls(cls, size: int) -> type[Self]:
        """Get query class for 中文 proofreading.

        Arguments:
            size: number of subtitles
        Returns:
            ZhongwenProofreadingQuery type with appropriate fields
        """
        query_fields = {}
        for idx in range(size):
            query_fields[f"zimu_{idx + 1}"] = (
                str,
                Field(..., description=f"第 {idx + 1} 条字幕"),
            )
        return create_model(f"{cls.__name__}_{size}", __base__=cls, **query_fields)
