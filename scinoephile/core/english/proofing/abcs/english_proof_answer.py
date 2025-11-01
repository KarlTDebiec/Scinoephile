#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for English proof answers."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, create_model

from scinoephile.core.abcs import Answer


class EnglishProofAnswer(Answer, ABC):
    """Abstract base class for English proof answers."""

    @classmethod
    def get_answer_cls(cls, size: int) -> type[EnglishProofAnswer]:
        """Get answer class for English proofing.

        Arguments:
            size: number of subtitles
        Returns:
            EnglishProofAnswer type with appropriate fields
        """
        answer_fields = {}
        for idx in range(size):
            answer_fields[f"revised_{idx + 1}"] = (
                str,
                Field("", description=f"Revised subtitle {idx + 1}"),
            )
            answer_fields[f"note_{idx + 1}"] = (
                str,
                Field(
                    "",
                    description=f"Note concerning revision of subtitle {idx + 1}",
                    max_length=1000,
                ),
            )
        return create_model(
            f"{cls.__name__}_{size}",
            __base__=EnglishProofAnswer,
            **answer_fields,
        )
