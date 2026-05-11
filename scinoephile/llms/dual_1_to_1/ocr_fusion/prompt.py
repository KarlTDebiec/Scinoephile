#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for OCR fusion dual 1 to 1 matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.dual_1_to_1 import Dual1To1Prompt

__all__ = ["OcrFusionPrompt"]


class OcrFusionPrompt(Dual1To1Prompt, ABC):
    """Text for LLM correspondence for OCR fusion dual 1 to 1 matters."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "Output subtitle text is required."
    """Error when output field is missing from answer."""

    note_missing_err: ClassVar[str] = "Explanation of output is required."
    """Error when note field is missing from answer."""
