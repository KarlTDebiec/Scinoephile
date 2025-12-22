#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR fusion dual track / single subtitle answers."""

from __future__ import annotations

from abc import ABC
from typing import Self

from pydantic import model_validator

from scinoephile.llms.dual_single import DualSingleAnswer

__all__ = ["OcrFusionAnswer"]


class OcrFusionAnswer(DualSingleAnswer, ABC):
    """OCR fusion dual track / single subtitle answers."""

    @model_validator(mode="after")
    def validate_answer(self) -> Self:
        """Ensure answer is internally valid."""
        if not getattr(self, self.prompt_cls.output, None):
            raise ValueError(self.prompt_cls.output_missing_err)
        if not getattr(self, self.prompt_cls.note, None):
            raise ValueError(self.prompt_cls.note_missing_err)
        return self
