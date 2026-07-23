#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Simple subtitle series synchronization comparisons."""

from __future__ import annotations

from scinoephile.core.subtitles import Series

__all__ = ["are_series_one_to_one"]


def are_series_one_to_one(one: Series, two: Series) -> bool:
    """Check whether two series are one-to-one matched.

    This is useful for preparing test cases, specifically for excluding one-to-one
    mappings, which are simple and not of interest for testing.

    Arguments:
        one: First series to compare
        two: Second series to compare
    Returns:
        Whether all subtitles are one-to-one matches between the two series
    """
    if len(one) != len(two):
        return False

    for one_sub, two_sub in zip(one, two):
        if one_sub.start != two_sub.start or one_sub.end != two_sub.end:
            return False

    return True
