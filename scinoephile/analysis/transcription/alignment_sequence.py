#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Convert subtitle references into timed alignment sequences."""

from __future__ import annotations

from math import isfinite

from scinoephile.analysis.alignment.timed_msa.models import Sequence
from scinoephile.core.subtitles.series import Series

__all__ = ["get_reference_sequence"]


def get_reference_sequence(
    name: str, series: Series, *, offset_seconds: float = 0.0
) -> Sequence:
    """Convert subtitle reference text into approximately timed characters.

    Arguments:
        name: stable reference row name
        series: reference subtitles on the complete source timeline
        offset_seconds: source time corresponding to alignment-local zero
    Returns:
        named reference sequence with alignment-local character timings
    Raises:
        ValueError: if the source offset is nonfinite or negative
    """
    if not isfinite(offset_seconds) or offset_seconds < 0.0:
        raise ValueError("Reference alignment offset must be finite and non-negative.")
    return Sequence.from_timed_texts(
        name,
        (
            (
                subtitle.text_with_newline,
                max(0.0, subtitle.start / 1000 - offset_seconds),
                subtitle.end / 1000 - offset_seconds,
            )
            for subtitle in series
            if subtitle.end / 1000 > offset_seconds
        ),
    )
