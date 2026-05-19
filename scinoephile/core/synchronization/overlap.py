#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle synchronization overlap matrix helpers."""

from __future__ import annotations

import numpy as np

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series

__all__ = [
    "get_overlap_string",
    "get_sync_overlap_matrix",
]


def get_overlap_string(overlap: np.ndarray) -> str:
    """Get string representation of overlap matrix between two series.

    1-indexed to match SRT.

    Arguments:
        overlap: Overlap matrix
    Returns:
        String representation of overlap matrix
    """
    max_items = 1_000_000
    matrix = np.array2string(
        overlap,
        precision=2,
        suppress_small=True,
        max_line_width=max_items,
        threshold=max_items,
        edgeitems=max_items,
    )
    matrix = matrix.replace("0.  ", "____").replace("[", " ").replace("]", " ")
    columns = [f"{j:>5}" for j in range(1, overlap.shape[1] + 1)]
    lines = ["  " + "".join(columns)]
    for i, row in enumerate(matrix.split("\n")):
        lines += [f"{i + 1:>2}" + row]
    return "\n".join(lines)


def get_sync_overlap_matrix(one: Series, two: Series) -> np.ndarray:
    """Quantify the overlap between two series and compile the results in a matrix.

    Arguments:
        one: First series
        two: Second series
    Returns:
        Two-dimensional array whose rows correspond to subtitle indexes within series
        one, whose columns correspond to subtitle indexes within series two, and whose
        values are the proportion of each subtitle in series two which overlaps with
        each subtitle in series one.
    Raises:
        ScinoephileError: if any subtitle has zero or negative duration
    """
    # Validate subtitle durations in series one
    for i, event in enumerate(one.events):
        duration = event.end - event.start
        if duration <= 0:
            raise ScinoephileError(
                f"Subtitle {i + 1} in series one has invalid duration "
                f"(start={event.start}, end={event.end}, duration={duration}). "
                f"Subtitles must have positive duration for synchronization."
            )

    # Validate subtitle durations in series two
    for i, event in enumerate(two.events):
        duration = event.end - event.start
        if duration <= 0:
            raise ScinoephileError(
                f"Subtitle {i + 1} in series two has invalid duration "
                f"(start={event.start}, end={event.end}, duration={duration}). "
                f"Subtitles must have positive duration for synchronization."
            )

    one_mu = np.array([e.start + (e.end - e.start) / 2 for e in one])
    one_sigma = np.array([(e.end - e.start) / 4 for e in one])
    two_mu = np.array([e.start + (e.end - e.start) / 2 for e in two])
    two_sigma = np.array([(e.end - e.start) / 4 for e in two])

    mu_diff_sq = (one_mu[:, np.newaxis] - two_mu[np.newaxis, :]) ** 2
    sigma_sq_sum = one_sigma[:, np.newaxis] ** 2 + two_sigma[np.newaxis, :] ** 2
    overlap = np.exp(-mu_diff_sq / (2 * sigma_sq_sum))

    return overlap
