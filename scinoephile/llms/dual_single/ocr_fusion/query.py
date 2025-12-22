#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR fusion dual track / single subtitle queries."""

from __future__ import annotations

from abc import ABC
from typing import Self

from pydantic import model_validator

from scinoephile.llms.dual_single import DualSingleQuery

__all__ = ["OcrFusionQuery"]


class OcrFusionQuery(DualSingleQuery, ABC):
    """OCR fusion dual track / single subtitle queries."""

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        source_one = getattr(self, self.prompt_cls.src_1, None)
        source_two = getattr(self, self.prompt_cls.src_2, None)
        if not source_one:
            raise ValueError(self.prompt_cls.src_1_missing_err)
        if not source_two:
            raise ValueError(self.prompt_cls.src_2_missing_err)
        if source_one == source_two:
            raise ValueError(self.prompt_cls.src_1_src_2_equal_err)
        return self
