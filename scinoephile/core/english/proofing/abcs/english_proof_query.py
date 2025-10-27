#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English proof queries."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, create_model

from scinoephile.core.abcs import Query


class EnglishProofQuery(Query, ABC):
    """Abstract base class for English proof queries."""

    @classmethod
    def get_query_cls(cls, size: int) -> type[EnglishProofQuery]:
        """Get query class for English proofing.

        Arguments:
            size: number of subtitles
        Returns:
            EnglishProofQuery type with appropriate fields
        """
        query_fields = {}
        for idx in range(size):
            query_fields[f"subtitle_{idx + 1}"] = (
                str,
                Field(..., description=f"Subtitle {idx + 1}"),
            )
        return create_model(
            f"{cls.__name__}_{size}",
            __base__=EnglishProofQuery,
            **query_fields,
        )
