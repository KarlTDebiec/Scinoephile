#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Diff classes for comparing subtitle text and series.

Package hierarchy (modules may import from any above):
* line_diff_kind
* line_diff
* series_diff
"""

from __future__ import annotations

from .line_diff import LineDiff
from .line_diff_kind import LineDiffKind
from .series_diff import SeriesDiff

__all__ = [
    "LineDiff",
    "LineDiffKind",
    "SeriesDiff",
]
