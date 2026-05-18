#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.synchronization.get_synced_series."""

from __future__ import annotations

import pytest

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.synchronization import (
    SyncTimingMode,
    get_synced_series,
    get_synced_series_from_groups,
)
from test.helpers import assert_series_equal


def _test_get_synced_series(one: Series, two: Series, expected: Series):
    """Test get_synced_series.

    Arguments:
        one: subtitles series one
        two: subtitles series two
        expected: expected output series
    """
    output = get_synced_series(one, two)
    assert_series_equal(output, expected)


def test_get_synced_series_does_not_overlap_union_timing():
    """Test sync never emits overlapping subtitles when inputs do not overlap."""
    one = Series(
        events=[
            Subtitle(start=1000, end=2000, text="A"),
            Subtitle(start=2100, end=3000, text="B"),
        ]
    )
    two = Series(
        events=[
            Subtitle(start=900, end=1900, text="1"),
            Subtitle(start=1950, end=2900, text="2"),
        ]
    )

    output = get_synced_series(one, two)

    assert output.events[0].text == "A\\N1"
    assert output.events[1].text == "B\\N2"
    assert output.events[1].start >= output.events[0].end


@pytest.mark.parametrize(
    ("timing_mode", "expected_times"),
    [
        (SyncTimingMode.TOP, [(1000, 2000), (2100, 3000)]),
        (SyncTimingMode.BOTTOM, [(900, 1900), (1950, 2900)]),
        (SyncTimingMode.OUTER, [(900, 1975), (1975, 3000)]),
    ],
)
def test_get_synced_series_uses_requested_timing_mode(
    timing_mode: SyncTimingMode,
    expected_times: list[tuple[int, int]],
):
    """Test sync uses the requested timing mode for paired subtitles."""
    one = Series(
        events=[
            Subtitle(start=1000, end=2000, text="A"),
            Subtitle(start=2100, end=3000, text="B"),
        ]
    )
    two = Series(
        events=[
            Subtitle(start=900, end=1900, text="1"),
            Subtitle(start=1950, end=2900, text="2"),
        ]
    )

    output = get_synced_series(one, two, timing_mode=timing_mode)

    assert [(event.start, event.end) for event in output.events] == expected_times
    assert [event.text for event in output.events] == ["A\\N1", "B\\N2"]


def test_get_synced_series_timing_mode_uses_available_timing_for_unpaired_subtitles():
    """Test unpaired subtitles keep their own timing in every timing mode."""
    one = Series(events=[Subtitle(start=1000, end=2000, text="A")])
    two = Series(events=[Subtitle(start=3000, end=4000, text="1")])
    groups = [([0], []), ([], [0])]

    for timing_mode in SyncTimingMode:
        output = get_synced_series_from_groups(
            one, two, groups, timing_mode=timing_mode
        )
        assert [(event.start, event.end) for event in output.events] == [
            (1000, 2000),
            (3000, 4000),
        ]
        assert [event.text for event in output.events] == ["A", "1"]


@pytest.mark.parametrize(
    ("timing_mode", "expected_times"),
    [
        (SyncTimingMode.TOP, [(1000, 1500), (1500, 2000)]),
        (SyncTimingMode.BOTTOM, [(900, 1300), (1400, 1900)]),
        (SyncTimingMode.OUTER, [(900, 1450), (1450, 2000)]),
    ],
)
def test_get_synced_series_splits_selected_timing_for_one_to_many_groups(
    timing_mode: SyncTimingMode,
    expected_times: list[tuple[int, int]],
):
    """Test one-to-many sync splits the selected timing interval."""
    one = Series(events=[Subtitle(start=1000, end=2000, text="A")])
    two = Series(
        events=[
            Subtitle(start=900, end=1300, text="1"),
            Subtitle(start=1400, end=1900, text="2"),
        ]
    )

    output = get_synced_series_from_groups(
        one, two, [([0], [0, 1])], timing_mode=timing_mode
    )

    assert [(event.start, event.end) for event in output.events] == expected_times
    assert [event.text for event in output.events] == ["A\\N1", "A\\N2"]


def test_get_synced_series_overlap_error_includes_event_context():
    """Test impossible overlap removal errors include adjacent event context."""
    one = Series(
        events=[
            Subtitle(start=1000, end=3000, text="A"),
            Subtitle(start=1000, end=1001, text="B"),
        ]
    )

    with pytest.raises(
        ScinoephileError,
        match=("events 1 and 2.*previous=1000-3000.*current=1000-1001"),
    ):
        get_synced_series_from_groups(one, Series(), [([0], []), ([1], [])])


def test_get_synced_series_kob(
    kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review: Series,
    kob_eng_ocr_fuse_clean_validate_review_flatten: Series,
    kob_zho_hans_eng: Series,
):
    """Test get_synced_series with KOB subtitles.

    Arguments:
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review:
          simplified standard Chinese subtitle fixture
        kob_eng_ocr_fuse_clean_validate_review_flatten: English subtitle fixture
        kob_zho_hans_eng: expected synced subtitles fixture
    """
    _test_get_synced_series(
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review,
        kob_eng_ocr_fuse_clean_validate_review_flatten,
        kob_zho_hans_eng,
    )


def test_get_synced_series_mlamd(
    mlamd_zho_hans_fuse_clean_validate_review_flatten: Series,
    mlamd_eng_fuse_clean_validate_review_flatten: Series,
    mlamd_zho_hans_eng: Series,
):
    """Test get_synced_series with MLAMD subtitles.

    Arguments:
        mlamd_zho_hans_fuse_clean_validate_review_flatten: simplified standard
          Chinese subtitle fixture
        mlamd_eng_fuse_clean_validate_review_flatten: English subtitle fixture
        mlamd_zho_hans_eng: expected synced subtitle fixture
    """
    _test_get_synced_series(
        mlamd_zho_hans_fuse_clean_validate_review_flatten,
        mlamd_eng_fuse_clean_validate_review_flatten,
        mlamd_zho_hans_eng,
    )


def test_get_synced_series_t(
    t_zho_hans_fuse_clean_validate_review_flatten: Series,
    t_eng_fuse_clean_validate_review_flatten: Series,
    t_zho_hans_eng: Series,
):
    """Test get_synced_series with T subtitles.

    Arguments:
        t_zho_hans_fuse_clean_validate_review_flatten: simplified standard Chinese
          subtitle fixture
        t_eng_fuse_clean_validate_review_flatten: English subtitle fixture
        t_zho_hans_eng: expected synced subtitle fixture
    """
    _test_get_synced_series(
        t_zho_hans_fuse_clean_validate_review_flatten,
        t_eng_fuse_clean_validate_review_flatten,
        t_zho_hans_eng,
    )
