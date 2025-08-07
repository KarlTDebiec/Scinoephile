#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 translation answers."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, create_model

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Answer


class TranslateAnswer(Answer, ABC):
    """Abstract base class for 粤文 translation answers."""

    @staticmethod
    def get_answer_cls(size: int, missing: tuple[int, ...]) -> type[TranslateAnswer]:
        """Get answer class for 粤文 translation.

        Arguments:
            size: Number of 中文 subtitles
            missing: Indices of 中文 subtitles that are missing 粤文
        Returns:
            Answer type with appropriate fields
        Raises:
            ScinoephileError: If missing indices are out of range
        """
        if any(m < 0 or m > size for m in missing):
            raise ScinoephileError(
                f"Missing indices must be in range 1 to {size}, got {missing}."
            )
        answer_fields = {}
        for zw_idx in range(size):
            if zw_idx in missing:
                answer_fields[f"yuewen_{zw_idx + 1}"] = (
                    str,
                    Field(..., description=f"Translated 粤文 of subtitle {zw_idx + 1}"),
                )
        return create_model(
            f"TranslateAnswer_{size}_{'-'.join(map(str, [m + 1 for m in missing]))}",
            __base__=TranslateAnswer,
            **answer_fields,
        )
