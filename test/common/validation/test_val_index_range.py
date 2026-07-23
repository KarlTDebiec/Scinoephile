#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_index_range."""

from __future__ import annotations

from pytest import raises

from scinoephile.common.validation import val_index_range


def test_val_index_range_builds_default_and_selected_ranges():
    """Test default and explicit processing ranges."""
    assert val_index_range(3) == range(3)
    assert val_index_range(3, 1, 2) == range(1, 2)
    assert val_index_range(3, 3) == range(3, 3)
    assert val_index_range(3, 4) == range(4, 3)


def test_val_index_range_rejects_invalid_boundaries():
    """Test invalid item counts and processing boundaries."""
    invalid_ranges = [
        (-1, 0, None, "item_count"),
        (3, -1, None, "start_at_idx"),
        (3, 0, -1, "stop_at_idx"),
        (3, 2, 1, "less than or equal"),
        (3, 0, 4, "stop_at_idx must not exceed"),
    ]
    for item_count, start_at_idx, stop_at_idx, message in invalid_ranges:
        with raises(ValueError, match=message):
            val_index_range(item_count, start_at_idx, stop_at_idx)
