#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for get_sync_overlap_matrix with zero and negative duration subtitles."""

from __future__ import annotations

import numpy as np
import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.synchronization import get_sync_overlap_matrix


def test_get_sync_overlap_matrix_zero_duration_series_one():
    """Test that zero-duration subtitle in series one raises clear error."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=100, end=100, text="B"))  # Zero duration
    one.events.append(Subtitle(start=100, end=200, text="C"))

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))
    two.events.append(Subtitle(start=100, end=200, text="2"))

    with pytest.raises(ScinoephileError) as exc_info:
        get_sync_overlap_matrix(one, two)

    error_msg = str(exc_info.value)
    assert "series one" in error_msg
    assert "invalid duration" in error_msg
    assert "Subtitle 2" in error_msg  # 1-indexed
    assert "start=100" in error_msg
    assert "end=100" in error_msg
    assert "duration=0" in error_msg


def test_get_sync_overlap_matrix_zero_duration_series_two():
    """Test that zero-duration subtitle in series two raises clear error."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=100, end=200, text="B"))

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))
    two.events.append(Subtitle(start=150, end=150, text="2"))  # Zero duration
    two.events.append(Subtitle(start=150, end=250, text="3"))

    with pytest.raises(ScinoephileError) as exc_info:
        get_sync_overlap_matrix(one, two)

    error_msg = str(exc_info.value)
    assert "series two" in error_msg
    assert "invalid duration" in error_msg
    assert "Subtitle 2" in error_msg  # 1-indexed
    assert "start=150" in error_msg
    assert "end=150" in error_msg
    assert "duration=0" in error_msg


def test_get_sync_overlap_matrix_negative_duration_series_one():
    """Test that negative-duration subtitle in series one raises clear error."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=200, end=150, text="B"))  # Negative duration
    one.events.append(Subtitle(start=200, end=300, text="C"))

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))
    two.events.append(Subtitle(start=100, end=200, text="2"))

    with pytest.raises(ScinoephileError) as exc_info:
        get_sync_overlap_matrix(one, two)

    error_msg = str(exc_info.value)
    assert "series one" in error_msg
    assert "invalid duration" in error_msg
    assert "Subtitle 2" in error_msg  # 1-indexed
    assert "start=200" in error_msg
    assert "end=150" in error_msg
    assert "duration=-50" in error_msg


def test_get_sync_overlap_matrix_negative_duration_series_two():
    """Test that negative-duration subtitle in series two raises clear error."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=100, end=200, text="B"))

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))
    two.events.append(Subtitle(start=300, end=200, text="2"))  # Negative duration
    two.events.append(Subtitle(start=300, end=400, text="3"))

    with pytest.raises(ScinoephileError) as exc_info:
        get_sync_overlap_matrix(one, two)

    error_msg = str(exc_info.value)
    assert "series two" in error_msg
    assert "invalid duration" in error_msg
    assert "Subtitle 2" in error_msg  # 1-indexed
    assert "start=300" in error_msg
    assert "end=200" in error_msg
    assert "duration=-100" in error_msg


def test_get_sync_overlap_matrix_valid_subtitles():
    """Test that valid subtitles produce expected overlap matrix without errors."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=100, end=200, text="B"))

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))
    two.events.append(Subtitle(start=100, end=200, text="2"))

    # Should not raise any errors
    overlap = get_sync_overlap_matrix(one, two)

    # Verify the overlap matrix has the correct shape
    assert overlap.shape == (2, 2)

    # Verify all values are finite (no inf or nan)
    assert np.all(np.isfinite(overlap))

    # Verify diagonal values are high (subtitles with same timing overlap strongly)
    assert overlap[0, 0] > 0.9
    assert overlap[1, 1] > 0.9


def test_get_sync_overlap_matrix_minimal_duration():
    """Test that very small but positive durations work correctly."""
    one = Series()
    one.events.append(Subtitle(start=0, end=1, text="A"))  # 1ms duration

    two = Series()
    two.events.append(Subtitle(start=0, end=1, text="1"))  # 1ms duration

    # Should not raise any errors
    overlap = get_sync_overlap_matrix(one, two)

    # Verify the overlap matrix has the correct shape
    assert overlap.shape == (1, 1)

    # Verify all values are finite (no inf or nan)
    assert np.all(np.isfinite(overlap))

    # Very small duration subtitles at same position should still have high overlap
    assert overlap[0, 0] > 0.9


def test_get_sync_overlap_matrix_first_subtitle_zero_duration():
    """Test error when first subtitle has zero duration."""
    one = Series()
    one.events.append(Subtitle(start=50, end=50, text="A"))  # Zero duration

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))

    with pytest.raises(ScinoephileError) as exc_info:
        get_sync_overlap_matrix(one, two)

    error_msg = str(exc_info.value)
    assert "Subtitle 1" in error_msg  # First subtitle, 1-indexed
    assert "series one" in error_msg


def test_get_sync_overlap_matrix_last_subtitle_zero_duration():
    """Test error when last subtitle has zero duration."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))
    one.events.append(Subtitle(start=100, end=200, text="B"))
    one.events.append(Subtitle(start=300, end=300, text="C"))  # Zero duration

    two = Series()
    two.events.append(Subtitle(start=0, end=100, text="1"))

    with pytest.raises(ScinoephileError) as exc_info:
        get_sync_overlap_matrix(one, two)

    error_msg = str(exc_info.value)
    assert "Subtitle 3" in error_msg  # Last subtitle, 1-indexed
    assert "series one" in error_msg


def test_get_sync_overlap_matrix_empty_series():
    """Test that empty series handle correctly without errors.

    Although get_sync_groups handles empty series before calling
    get_sync_overlap_matrix, we test the function directly to ensure
    it handles empty input gracefully.
    """
    one = Series()
    two = Series()

    # Empty series should return empty matrix
    overlap = get_sync_overlap_matrix(one, two)
    assert overlap.shape == (0, 0)


def test_get_sync_overlap_matrix_one_empty_series():
    """Test overlap matrix with one empty series."""
    one = Series()
    one.events.append(Subtitle(start=0, end=100, text="A"))

    two = Series()

    # Empty series two should return empty matrix
    overlap = get_sync_overlap_matrix(one, two)
    assert overlap.shape == (1, 0)
