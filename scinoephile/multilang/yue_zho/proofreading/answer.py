#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for 粤文 vs. 中文 proofreading answers."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.llms.dual_single import DualSingleAnswer

from .prompts import YueZhoHansProofreadingPrompt

__all__ = ["YueZhoProofreadingAnswer"]


class YueZhoProofreadingAnswer(DualSingleAnswer, ABC):
    """ABC for 粤文 vs. 中文 proofreading answers."""

    prompt_cls: ClassVar[type[YueZhoHansProofreadingPrompt]]
    """Text for LLM correspondence."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        output = getattr(self, self.prompt_cls.output, None)
        note = getattr(self, self.prompt_cls.note, None)
        if not output and not note:
            raise ValueError(self.prompt_cls.output_missing_note_missing_err)
        return self
