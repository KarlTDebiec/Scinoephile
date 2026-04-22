#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Chinese (zho) text.

Package hierarchy (modules may import from any above):
* cleaning / conversion / flattening / ocr_validation
* prompts
* ocr_fusion / block_review
"""

from __future__ import annotations

from .cleaning import get_zho_cleaned
from .conversion import get_zho_converted, is_simplified, is_traditional
from .flattening import get_zho_flattened
from .ocr_fusion import get_zho_ocr_fused
from .ocr_validation import validate_zho_ocr
from .block_review import get_zho_reviewed

__all__ = [
    "get_zho_cleaned",
    "get_zho_converted",
    "get_zho_flattened",
    "get_zho_ocr_fused",
    "get_zho_reviewed",
    "is_simplified",
    "is_traditional",
    "validate_zho_ocr",
]
