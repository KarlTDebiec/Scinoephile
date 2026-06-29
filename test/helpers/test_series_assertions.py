#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle series assertions."""

from __future__ import annotations

from typing import cast

from pysubs2 import SSAFile
from pytest import raises

from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import assert_series_equal


def test_assert_series_equal_passes_for_matching_series():
    """Test subtitle series assertion passes for matching series."""
    actual = Series(events=[Subtitle(start=1000, end=2000, text="same")])
    expected = Series(events=[Subtitle(start=1000, end=2000, text="same")])

    assert_series_equal(actual, expected)


def test_assert_series_equal_reports_mismatching_subtitle():
    """Test subtitle series assertion reports mismatching subtitle details."""
    actual = Series(
        events=[
            Subtitle(start=1000, end=2000, text="same"),
            Subtitle(start=3000, end=4000, text="actual"),
        ]
    )
    expected = Series(
        events=[
            Subtitle(start=1000, end=2000, text="same"),
            Subtitle(start=3000, end=4500, text="expected"),
        ]
    )

    with raises(AssertionError) as excinfo:
        assert_series_equal(actual, expected)

    message = str(excinfo.value)
    assert "Subtitle event 2 mismatch" in message
    assert "Actual: start=3000, end=4000, text='actual'" in message
    assert "Expected: start=3000, end=4500, text='expected'" in message


def test_assert_series_equal_rejects_non_series_actual():
    """Test subtitle series assertion rejects non-series actual values."""
    actual = [Subtitle(start=1000, end=2000, text="same")]
    expected = Series(events=[Subtitle(start=1000, end=2000, text="same")])

    with raises(AssertionError) as excinfo:
        assert_series_equal(cast(SSAFile, actual), expected)

    assert str(excinfo.value) == "actual is not a subtitle series: list"


def test_assert_series_equal_rejects_non_series_expected():
    """Test subtitle series assertion rejects non-series expected values."""
    actual = Series(events=[Subtitle(start=1000, end=2000, text="same")])
    expected = [Subtitle(start=1000, end=2000, text="same")]

    with raises(AssertionError) as excinfo:
        assert_series_equal(actual, cast(SSAFile, expected))

    assert str(excinfo.value) == "expected is not a subtitle series: list"
