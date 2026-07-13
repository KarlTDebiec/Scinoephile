#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for max_cutoff handling in get_sync_groups."""

from __future__ import annotations

from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.synchronization import get_sync_groups


def test_get_sync_groups_preserves_subtitles_when_other_series_is_empty():
    """Test empty-series handling preserves every subtitle from the other series."""
    empty = Series()
    populated = Series(
        events=[
            Subtitle(start=0, end=100, text="A"),
            Subtitle(start=200, end=300, text="B"),
        ]
    )

    assert get_sync_groups(empty, populated) == [([], [0]), ([], [1])]
    assert get_sync_groups(populated, empty) == [([0], []), ([1], [])]
    assert get_sync_groups(empty, empty) == []


def test_get_sync_groups_exceeds_max_cutoff():
    """Test that get_sync_groups raises error when max_cutoff is exceeded.

    This test creates a pathological case where sync groups cannot be computed
    even with high cutoff values, ensuring the function terminates with an error.
    """
    # Create two series with highly overlapping subtitles that create conflicts
    # These subtitles all have identical timing, which creates an unresolvable
    # many-to-many mapping that cannot be cleaned up by increasing the cutoff
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=0, end=100, text="B"))
    one.events.append(Subtitle(start=0, end=100, text="C"))

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))
    two.events.append(Subtitle(start=0, end=100, text="2"))
    two.events.append(Subtitle(start=0, end=100, text="3"))

    # This should raise ScinoephileError due to max_cutoff being exceeded
    with raises(ScinoephileError) as exc_info:
        get_sync_groups(one, two)

    # Verify the error message contains expected information
    error_msg = str(exc_info.value)
    assert "cutoff exceeded" in error_msg
    assert "1.0" in error_msg or "1.01" in error_msg
    assert "shape" in error_msg.lower()


def test_get_sync_groups_converges_below_max_cutoff():
    """Test that get_sync_groups works correctly when it converges normally.

    This ensures that the max_cutoff check does not interfere with normal operation.
    """
    # Create two series with simple one-to-one mapping
    one = Series()
    one.events.append(Subtitle(start=0, end=10, text="A"))
    one.events.append(Subtitle(start=15, end=25, text="B"))

    two = Series()
    two.events.append(Subtitle(start=0, end=10, text="1"))
    two.events.append(Subtitle(start=15, end=25, text="2"))

    # This should succeed without raising an error
    sync_groups = get_sync_groups(one, two)

    # Verify we got the expected sync groups
    assert len(sync_groups) == 2
    assert sync_groups[0] == ([0], [0])
    assert sync_groups[1] == ([1], [1])


def test_get_sync_groups_sorts_unpaired_groups_by_timing():
    """Test unpaired sync groups are sorted by timing when indexes cannot compare."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=2_000_000, end=2_000_100, text="B"))
    one.events.append(Subtitle(start=4_000_000, end=4_000_100, text="C"))

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))
    two.events.append(Subtitle(start=1_000_000, end=1_000_100, text="2"))
    two.events.append(Subtitle(start=4_000_000, end=4_000_100, text="3"))

    sync_groups = get_sync_groups(one, two)

    assert sync_groups == [
        ([0], [0]),
        ([], [1]),
        ([1], []),
        ([2], [2]),
    ]
