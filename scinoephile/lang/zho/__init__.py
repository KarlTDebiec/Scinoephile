#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to 中文 text.

Package hierarchy (modules may import from any above):
* conversion
* prompts
* cleaning / flattening / ocr_fusion / proofreading
"""

from __future__ import annotations

from .cleaning import get_zho_cleaned
from .conversion import get_zho_converted
from .flattening import get_zho_flattened
from .ocr_fusion import get_zho_ocr_fused
from .proofreading import get_zho_proofread

__all__ = [
    "get_zho_cleaned",
    "get_zho_converted",
    "get_zho_flattened",
    "get_zho_ocr_fused",
    "get_zho_proofread",
]
