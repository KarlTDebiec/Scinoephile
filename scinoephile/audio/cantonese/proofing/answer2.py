#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for 粤文 transcription proofing answers."""

from __future__ import annotations

from abc import ABC
from functools import cache
from typing import ClassVar, Self

from pydantic import Field, create_model, model_validator

from scinoephile.core.llms import Answer2
from scinoephile.core.models import get_cls_name

from .prompt2 import ProofingPrompt2

__all__ = ["ProofingAnswer2"]


class ProofingAnswer2(Answer2, ABC):
    """Abstract base class for 粤文 transcription proofing answers."""

    prompt_cls: ClassVar[type[ProofingPrompt2]]
    """Text strings to be used for corresponding with LLM."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        yuewen_proofread = getattr(self, "yuewen_proofread", None)
        note = getattr(self, "note", None)
        if not yuewen_proofread and not note:
            raise ValueError(self.prompt_cls.yuewen_proofread_and_note_missing_error)
        return self

    @classmethod
    @cache
    def get_answer_cls(
        cls,
        prompt_cls: type[ProofingPrompt2] = ProofingPrompt2,
    ) -> type[Self]:
        """Get concrete answer class with provided configuartion.

        Arguments:
            prompt_cls: Prompt providing descriptions and messages
        Returns:
            Answer type with appropriate configuration
        """
        name = get_cls_name(cls.__name__, prompt_cls.__name__)
        fields = {
            "yuewen_proofread": (
                str,
                Field("", description=prompt_cls.yuewen_proofread_description),
            ),
            "note": (str, Field("", description=prompt_cls.note_description)),
        }

        model = create_model(name, __base__=cls, __module__=cls.__module__, **fields)
        model.prompt_cls = prompt_cls
        return model
