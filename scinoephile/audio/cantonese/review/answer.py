#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription review answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import Any, ClassVar

from pydantic import Field, create_model

from scinoephile.core.abcs import Answer

from .prompt import ReviewPrompt

__all__ = ["ReviewAnswer"]


class ReviewAnswer(Answer, ABC):
    """Abstract base class for 粤文 transcription review answers."""

    text: ClassVar[type[ReviewPrompt]]
    """Text strings to be used for corresponding with LLM."""

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        size: int,
        text: type[ReviewPrompt] = ReviewPrompt,
    ) -> type[ReviewAnswer]:
        """Get concrete answer class with provided configuration.

        Arguments:
            size: number of subtitles
            text: Prompt providing descriptions and messages
        Returns:
            Answer type with appropriate configuration
        """
        fields: dict[str, Any] = {}
        for idx in range(size):
            fields[f"yuewen_revised_{idx + 1}"] = (
                str,
                Field("", description=f"Revised 粤文 of subtitle {idx + 1}"),
            )
            fields[f"note_{idx + 1}"] = (
                str,
                Field(
                    "",
                    description=f"Note concerning revision of {idx + 1}",
                    max_length=1000,
                ),
            )
        return create_model(
            f"{cls.__name__}_{size}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ReviewPrompt]], text),
            **fields,
        )
