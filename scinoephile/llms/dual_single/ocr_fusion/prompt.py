#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for OCR fusion dual track / single subtitle matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.dual_single import DualSinglePrompt

__all__ = ["OcrFusionPrompt"]


class OcrFusionPrompt(DualSinglePrompt, ABC):
    """Text for LLM correspondence for OCR fusion dual track / single subtitles."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "Output subtitle text is required."
    """Error when output field is missing from answer."""

    note_missing_err: ClassVar[str] = "Explanation of output is required."
    """Error when note field is missing from answer."""
