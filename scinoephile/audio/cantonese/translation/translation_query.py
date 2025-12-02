#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 translation queries."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Query


class TranslationQuery(Query, ABC):
    """Abstract base class for 粤文 translation queries."""

    @classmethod
    def get_query_cls(
        cls, size: int, missing: tuple[int, ...]
    ) -> type[TranslationQuery]:
        """Get query class for 粤文 translation.

        Arguments:
            size: Number of 中文 subtitles
            missing: Indices of 中文 subtitles that are missing 粤文
        Returns:
            Query type with appropriate fields
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )
        query_fields = {}
        for zw_idx in range(size):
            query_fields[f"zhongwen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Known 中文 of subtitle {zw_idx + 1}"),
            )
            if zw_idx not in missing:
                query_fields[f"yuewen_{zw_idx + 1}"] = (
                    str,
                    Field(
                        ..., description=f"Transcribed 粤文 of subtitle {zw_idx + 1}"
                    ),
                )
        name = f"{cls.__name__}_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}"
        return create_model(name[:64], __base__=TranslationQuery, **query_fields)
