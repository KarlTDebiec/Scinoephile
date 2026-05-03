#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Diff classes for comparing subtitle text and series."""

from __future__ import annotations

from .alignment_series_diff import AlignmentSeriesDiff
from .line_diff import LineDiff
from .line_diff_kind import LineDiffKind
from .series_diff import SeriesDiff

__all__ = [
    "AlignmentSeriesDiff",
    "LineDiff",
    "LineDiffKind",
    "SeriesDiff",
]
