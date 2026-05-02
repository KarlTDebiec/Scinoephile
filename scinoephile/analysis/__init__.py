#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Analysis code for comparing subtitle series.

This module may import from: common, core

Hierarchy within module (lower may import from higher)::
* character_error_rate
* line_diff_kind / replace_cursor
* line_diff
* series_diff
"""

from __future__ import annotations

from .character_error_rate import get_series_cer, get_text_cer
from .character_error_rate_result import CharacterErrorRateResult
from .line_diff import LineDiff
from .series_diff import SeriesDiff

__all__ = [
    "CharacterErrorRateResult",
    "LineDiff",
    "SeriesDiff",
    "get_series_cer",
    "get_text_cer",
]
