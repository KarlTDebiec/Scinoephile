#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription proofing answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.audio.cantonese.proofing.proofing_llm_text import ProofingLLMText
from scinoephile.core.abcs import Answer


class ProofingAnswer(Answer, ABC):
    """Abstract base class for 粤文 transcription proofing answers."""

    text: ClassVar[type[ProofingLLMText]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        if not self.yuewen_proofread and not self.note:
            raise ValueError(self.text.yuewen_proofread_and_note_missing_error)
        return self

    @classmethod
    @cache
    def get_answer_cls(
        cls, text: type[ProofingLLMText] = ProofingLLMText
    ) -> type[Self]:
        """Get concrete answer class with provided text.

        Arguments:
            text: LLMText providing descriptions and messages
        Returns:
            Answer type with appropriate fields and text
        """
        fields = {
            "yuewen_proofread": (
                str,
                Field("", description=text.yuewen_proofread_description),
            ),
            "note": (str, Field("", description=text.note_description)),
        }
        return create_model(
            f"{cls.__name__}_{text.__name__}",
            __base__=cls,
            __module__=cls.__module__,
            text=(ClassVar[type[ProofingLLMText]], text),
            **fields,
        )
