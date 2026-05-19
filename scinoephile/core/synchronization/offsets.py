#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle synchronization offset statistics."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median, pstdev

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.pairs import get_block_pairs_by_pause
from scinoephile.core.subtitles import Series, Subtitle

from .groups import get_sync_groups

__all__ = [
    "SyncOffsetDatum",
    "SyncOffsetStats",
    "get_sync_offset_stats",
]


@dataclass(frozen=True)
class SyncOffsetDatum:
    """One paired sync group used for subtitle offset estimation."""

    block_index: int
    """Zero-based block index containing the paired sync group."""

    group_index: int
    """Zero-based sync group index within the block."""

    anchor_indexes: tuple[int, ...]
    """Block-local subtitle indexes from the anchor series."""

    mobile_indexes: tuple[int, ...]
    """Block-local subtitle indexes from the mobile series."""

    offset_ms: float
    """Mobile group midpoint minus anchor group midpoint, in milliseconds."""


@dataclass(frozen=True)
class SyncOffsetStats:
    """Statistics for subtitle offset estimation."""

    sample_count: int
    """Number of paired sync groups included in the estimate."""

    skipped_group_count: int
    """Number of unpaired sync groups skipped during estimation."""

    mean_ms: float
    """Mean mobile-minus-anchor offset, in milliseconds."""

    median_ms: float
    """Median mobile-minus-anchor offset, in milliseconds."""

    stdev_ms: float
    """Population standard deviation of offsets, in milliseconds."""

    min_ms: float
    """Minimum mobile-minus-anchor offset, in milliseconds."""

    max_ms: float
    """Maximum mobile-minus-anchor offset, in milliseconds."""

    samples: tuple[SyncOffsetDatum, ...]
    """Offset samples included in the estimate."""


def get_sync_offset_stats(
    anchor: Series,
    mobile: Series,
    sync_cutoff: float = 0.16,
    pause_length: int = 3000,
) -> SyncOffsetStats:
    """Estimate subtitle offset statistics between already-close series.

    The offset is computed as mobile timing minus anchor timing. Positive values mean
    the mobile series is later than the anchor series and should be shifted earlier to
    align with it.

    Arguments:
        anchor: series used as timing reference
        mobile: series to compare against the anchor
        sync_cutoff: initial overlap cutoff used to form sync groups
        pause_length: pause length in milliseconds used to split subtitle blocks
    Returns:
        offset statistics computed from paired sync groups
    Raises:
        ScinoephileError: if no paired sync groups are available
    """
    samples: list[SyncOffsetDatum] = []
    skipped_group_count = 0
    block_pairs = get_block_pairs_by_pause(anchor, mobile, pause_length=pause_length)

    for block_index, (anchor_block, mobile_block) in enumerate(block_pairs):
        if not anchor_block.events:
            groups = [([], [i]) for i in range(len(mobile_block))]
        elif not mobile_block.events:
            groups = [([i], []) for i in range(len(anchor_block))]
        else:
            groups = get_sync_groups(anchor_block, mobile_block, cutoff=sync_cutoff)

        for group_index, (anchor_indexes, mobile_indexes) in enumerate(groups):
            if not anchor_indexes or not mobile_indexes:
                skipped_group_count += 1
                continue

            anchor_subs = [anchor_block.events[i] for i in anchor_indexes]
            mobile_subs = [mobile_block.events[i] for i in mobile_indexes]
            offset_ms = _get_subtitle_group_midpoint(
                mobile_subs
            ) - _get_subtitle_group_midpoint(anchor_subs)
            samples.append(
                SyncOffsetDatum(
                    block_index=block_index,
                    group_index=group_index,
                    anchor_indexes=tuple(anchor_indexes),
                    mobile_indexes=tuple(mobile_indexes),
                    offset_ms=offset_ms,
                )
            )

    if not samples:
        raise ScinoephileError(
            "No paired sync groups found; cannot estimate subtitle offset"
        )

    offsets = [sample.offset_ms for sample in samples]
    return SyncOffsetStats(
        sample_count=len(samples),
        skipped_group_count=skipped_group_count,
        mean_ms=mean(offsets),
        median_ms=median(offsets),
        stdev_ms=pstdev(offsets),
        min_ms=min(offsets),
        max_ms=max(offsets),
        samples=tuple(samples),
    )


def _get_subtitle_group_midpoint(subtitles: list[Subtitle]) -> float:
    """Get midpoint of a subtitle group span.

    Arguments:
        subtitles: subtitle group
    Returns:
        midpoint of the group span in milliseconds
    """
    start = min(subtitle.start for subtitle in subtitles)
    end = max(subtitle.end for subtitle in subtitles)
    return start + (end - start) / 2
