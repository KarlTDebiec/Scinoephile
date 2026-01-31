#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Analysis code for comparing subtitle series.

Module hierarchy (within scinoephile):
This module may import from: common, core
"""

from __future__ import annotations

from typing import Unpack

from scinoephile.core.subtitles import Series

from .line_diff import LineDiff
from .series_diff import SeriesDiff, SeriesDiffKwargs

__all__ = ["get_series_diff"]


def get_series_diff(
    one: Series,
    two: Series,
    **kwargs: Unpack[SeriesDiffKwargs],
) -> list[LineDiff]:
    """Compare two subtitle series by line content.

    Arguments:
        one: first subtitle series
        two: second subtitle series
        **kwargs: additional keyword arguments for SeriesDiff
    Returns:
        list of difference messages
    """
    return SeriesDiff(one, two, **kwargs).msgs
