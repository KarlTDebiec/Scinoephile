#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to validation."""

from __future__ import annotations

from scinoephile.core.subtitles import Series
from scinoephile.core.validation.line_diff import LineDiff
from scinoephile.core.validation.series_diff import SeriesDiff

__all__ = ["get_series_diff"]


def get_series_diff(
    one: Series,
    two: Series,
    **kwargs: object,
) -> list[LineDiff]:
    """Compare two subtitle series by line content.

    Arguments:
        one: First subtitle series
        two: Second subtitle series
        **kwargs: additional keyword arguments for SeriesDiff
    Returns:
        list of difference messages
    """
    return SeriesDiff(one, two, **kwargs).msgs
