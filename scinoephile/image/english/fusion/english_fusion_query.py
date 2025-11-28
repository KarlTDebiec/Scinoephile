#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for English OCR fusion."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, model_validator

from scinoephile.core.abcs import Query


class EnglishFusionQuery(Query, ABC):
    """Query for English OCR fusion."""

    lens: str = Field(..., description="Subtitle Text OCRed using Google Lens")
    tesseract: str = Field(..., description="Subtitle Text OCRed using Tesseract")

    @model_validator(mode="after")
    def validate_query(self) -> EnglishFusionQuery:
        """Ensure query is internally valid."""
        if not self.lens:
            raise ValueError("Subtitle Text OCRed using Google Lens is required。")
        if not self.tesseract:
            raise ValueError("Subtitle Text OCRed using Tesseract is required。")
        if self.lens == self.tesseract:
            raise ValueError(
                "Subtitle Text OCRed using Google Lens and Tesseract must differ。"
            )
        return self
