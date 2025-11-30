#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 review answers."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, create_model

from scinoephile.core.abcs import Answer


class ReviewAnswer(Answer, ABC):
    """Abstract base class for 粤文 review answers."""

    @classmethod
    def get_answer_cls(cls, size: int) -> type[ReviewAnswer]:
        """Get answer class for 粤文 review.

        Arguments:
            size: Number of 中文 subtitles
        Returns:
            Answer type with appropriate fields
        """
        answer_fields = {}
        for zw_idx in range(size):
            answer_fields[f"yuewen_revised_{zw_idx + 1}"] = (
                str,
                Field("", description=f"Revised 粤文 of subtitle {zw_idx + 1}"),
            )
            answer_fields[f"note_{zw_idx + 1}"] = (
                str,
                Field(
                    "",
                    description=f"Note concerning revision of {zw_idx + 1}",
                    max_length=1000,
                ),
            )
        return create_model(
            f"{cls.__name__}_{size}", __base__=ReviewAnswer, **answer_fields
        )
