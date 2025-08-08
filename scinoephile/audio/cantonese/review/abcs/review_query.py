#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 review queries."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, create_model

from scinoephile.core.abcs import Query


class ReviewQuery(Query, ABC):
    """Abstract base class for 粤文 review queries."""

    @classmethod
    def get_query_cls(cls, size: int) -> type[ReviewQuery]:
        """Get query class for 粤文 review.

        Arguments:
            size: Number of 中文 subtitles
        Returns:
            Query type with appropriate fields
        """
        query_fields = {}
        for zw_idx in range(size):
            query_fields[f"zhongwen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Known 中文 of subtitle {zw_idx + 1}"),
            )
            query_fields[f"yuewen_{zw_idx + 1}"] = (
                str,
                Field(..., description=f"Transcribed 粤文 of subtitle {zw_idx + 1}"),
            )
        return create_model(
            f"{cls.__name__}_{size}",
            __base__=ReviewQuery,
            **query_fields,
        )
