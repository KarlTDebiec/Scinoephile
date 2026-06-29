#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of sync offset statistics."""

from __future__ import annotations

from pytest import approx, raises

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.synchronization import get_sync_offset_stats


def test_get_sync_offset_stats_uses_paired_group_midpoints():
    """Test offset statistics use paired subtitle midpoint differences."""
    anchor = Series(events=[Subtitle(start=1000, end=2000, text="A")])
    mobile = Series(events=[Subtitle(start=1250, end=2250, text="1")])

    stats = get_sync_offset_stats(anchor, mobile)

    assert stats.sample_count == 1
    assert stats.skipped_group_count == 0
    assert stats.mean_ms == approx(250.0)
    assert stats.median_ms == approx(250.0)
    assert stats.stdev_ms == approx(0.0)
    assert stats.min_ms == approx(250.0)
    assert stats.max_ms == approx(250.0)
    assert stats.samples[0].offset_ms == approx(250.0)


def test_get_sync_offset_stats_uses_group_span_midpoints_for_many_to_one():
    """Test many-to-one groups compare subtitle group span midpoints."""
    anchor = Series(
        events=[
            Subtitle(start=0, end=1000, text="A"),
            Subtitle(start=1100, end=2100, text="B"),
        ]
    )
    mobile = Series(events=[Subtitle(start=100, end=2200, text="1")])

    stats = get_sync_offset_stats(anchor, mobile)

    assert stats.sample_count == 1
    assert stats.mean_ms == approx(100.0)
    assert stats.samples[0].anchor_indexes == (0, 1)
    assert stats.samples[0].mobile_indexes == (0,)


def test_get_sync_offset_stats_skips_unpaired_groups():
    """Test unpaired sync groups are counted but not included in offset samples."""
    anchor = Series(
        events=[
            Subtitle(start=1000, end=2000, text="A"),
            Subtitle(start=7000, end=8000, text="B"),
        ]
    )
    mobile = Series(events=[Subtitle(start=1250, end=2250, text="1")])

    stats = get_sync_offset_stats(anchor, mobile)

    assert stats.sample_count == 1
    assert stats.skipped_group_count == 1
    assert stats.mean_ms == approx(250.0)


def test_get_sync_offset_stats_skips_mobile_only_blocks():
    """Test mobile-only blocks are counted as skipped offset groups."""
    anchor = Series(events=[Subtitle(start=1000, end=2000, text="A")])
    mobile = Series(
        events=[
            Subtitle(start=1250, end=2250, text="1"),
            Subtitle(start=7000, end=8000, text="2"),
            Subtitle(start=8100, end=9000, text="3"),
        ]
    )

    stats = get_sync_offset_stats(anchor, mobile)

    assert stats.sample_count == 1
    assert stats.skipped_group_count == 2
    assert stats.mean_ms == approx(250.0)


def test_get_sync_offset_stats_raises_when_no_paired_groups():
    """Test offset calculation fails clearly when no paired groups are available."""
    anchor = Series(events=[Subtitle(start=1000, end=2000, text="A")])
    mobile = Series(events=[Subtitle(start=7000, end=8000, text="1")])

    with raises(ScinoephileError, match="No paired sync groups"):
        get_sync_offset_stats(anchor, mobile)
