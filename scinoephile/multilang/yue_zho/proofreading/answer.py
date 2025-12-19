#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Proofreading-specific DualSingle answer."""

from __future__ import annotations

from typing import ClassVar, Self

from pydantic import model_validator

from scinoephile.llms.dual_single import DualSingleAnswer, DualSinglePrompt

__all__ = ["YueZhoProofreadingAnswer"]


class YueZhoProofreadingAnswer(DualSingleAnswer):
    """DualSingle answer that permits empty output and optional notes."""

    prompt_cls: ClassVar[type[DualSinglePrompt]]

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Allow empty output but require fields to be present."""
        if getattr(self, self.prompt_cls.output_field, None) is None:
            raise ValueError(self.prompt_cls.output_missing_error)
        if getattr(self, self.prompt_cls.note_field, None) is None:
            raise ValueError(self.prompt_cls.note_missing_error)
        return self
