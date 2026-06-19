#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OCR validation for image subtitles.

Package hierarchy (modules may import from any above):
* char_cursor / csv
* char_dims / char_grp_dims / char_pair_gaps
* gap_cursor
* validation_manager
"""

from __future__ import annotations

from .validation_manager import MAX_CHAR_DIM_BBOXES, ValidationManager

__all__ = [
    "MAX_CHAR_DIM_BBOXES",
    "ValidationManager",
]
