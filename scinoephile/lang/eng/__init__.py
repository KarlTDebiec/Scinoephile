#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English (eng) text.

Package hierarchy (modules may import from any above):
* prompts
* cleaning / flattening / ocr_fusion / proofreading
"""

from __future__ import annotations

from .cleaning import get_eng_cleaned
from .flattening import get_eng_flattened
from .ocr_fusion import get_eng_ocr_fused
from .ocr_validation import validate_eng_ocr
from .proofreading import get_eng_proofread

__all__ = [
    "get_eng_cleaned",
    "get_eng_flattened",
    "get_eng_ocr_fused",
    "get_eng_proofread",
    "validate_eng_ocr",
]
