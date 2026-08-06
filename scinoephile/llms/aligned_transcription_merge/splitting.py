#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared-pause splitting for aligned transcription merge requests."""

from __future__ import annotations

from collections.abc import Sequence

__all__ = ["get_alignment_content_spans"]


def get_alignment_content_spans(
    shared_pause_columns: Sequence[bool], separator_columns: int
) -> tuple[tuple[int, int], ...]:
    """Get content spans between long shared-pause separators.

    Arguments:
        shared_pause_columns: whether each alignment column is a shared pause
        separator_columns: minimum consecutive pauses separating content spans
    Returns:
        inclusive-start, exclusive-end content spans
    Raises:
        ValueError: if the separator threshold is not positive
    """
    if separator_columns <= 0:
        raise ValueError("Alignment separator column count must be positive.")

    separator_spans = []
    run_start: int | None = None
    for column_idx, is_shared_pause in enumerate((*shared_pause_columns, False)):
        if is_shared_pause:
            if run_start is None:
                run_start = column_idx
            continue
        if run_start is None:
            continue
        if column_idx - run_start >= separator_columns:
            separator_spans.append((run_start, column_idx))
        run_start = None

    content_spans = []
    content_start = 0
    for separator_start, separator_end in separator_spans:
        if content_start < separator_start:
            content_spans.append((content_start, separator_start))
        content_start = separator_end
    if content_start < len(shared_pause_columns):
        content_spans.append((content_start, len(shared_pause_columns)))
    return tuple(content_spans)
