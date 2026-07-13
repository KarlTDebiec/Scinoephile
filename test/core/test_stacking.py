#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.stacking.get_stacked_series."""

from __future__ import annotations

from pytest import FixtureRequest, param, raises

from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.stacking import (
    StackTimingMode,
    get_stacked_series,
    get_stacked_series_from_groups,
)
from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import assert_series_equal, parametrize


def test_get_stacked_series_preserves_nonempty_series_when_other_is_empty():
    """Test stacking keeps subtitles when either input series is empty."""
    empty = Series()
    populated = Series(
        events=[
            Subtitle(start=1000, end=2000, text="A"),
            Subtitle(start=3000, end=4000, text="B"),
        ]
    )

    for one, two in [(empty, populated), (populated, empty)]:
        output = get_stacked_series(one, two)
        assert [(event.start, event.end, event.text) for event in output.events] == [
            (1000, 2000, "A"),
            (3000, 4000, "B"),
        ]


def test_get_stacked_series_does_not_overlap_union_timing():
    """Test stack never emits overlapping subtitles when inputs do not overlap."""
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

    output = get_stacked_series(one, two)

    assert output.events[0].text == "A\\N1"
    assert output.events[1].text == "B\\N2"
    assert output.events[1].start >= output.events[0].end


@parametrize(
    ("timing_mode", "expected_times"),
    [
        (StackTimingMode.TOP, [(1000, 2000), (2100, 3000)]),
        (StackTimingMode.BOTTOM, [(900, 1900), (1950, 2900)]),
        (StackTimingMode.OUTER, [(900, 1975), (1975, 3000)]),
    ],
)
def test_get_stacked_series_uses_requested_timing_mode(
    timing_mode: StackTimingMode,
    expected_times: list[tuple[int, int]],
):
    """Test stack uses the requested timing mode for paired subtitles."""
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

    output = get_stacked_series(one, two, timing_mode=timing_mode)

    assert [(event.start, event.end) for event in output.events] == expected_times
    assert [event.text for event in output.events] == ["A\\N1", "B\\N2"]


def test_get_stacked_series_timing_mode_uses_available_timing_for_unpaired_subtitles():
    """Test unpaired subtitles keep their own timing in every timing mode."""
    one = Series(events=[Subtitle(start=1000, end=2000, text="A")])
    two = Series(events=[Subtitle(start=3000, end=4000, text="1")])
    groups = [([0], []), ([], [0])]

    for timing_mode in StackTimingMode:
        output = get_stacked_series_from_groups(
            one, two, groups, timing_mode=timing_mode
        )
        assert [(event.start, event.end) for event in output.events] == [
            (1000, 2000),
            (3000, 4000),
        ]
        assert [event.text for event in output.events] == ["A", "1"]


@parametrize(
    ("timing_mode", "expected_times"),
    [
        (StackTimingMode.TOP, [(1000, 1500), (1500, 2000)]),
        (StackTimingMode.BOTTOM, [(900, 1300), (1400, 1900)]),
        (StackTimingMode.OUTER, [(900, 1450), (1450, 2000)]),
    ],
)
def test_get_stacked_series_splits_selected_timing_for_one_to_many_groups(
    timing_mode: StackTimingMode,
    expected_times: list[tuple[int, int]],
):
    """Test one-to-many stack splits the selected timing interval."""
    one = Series(events=[Subtitle(start=1000, end=2000, text="A")])
    two = Series(
        events=[
            Subtitle(start=900, end=1300, text="1"),
            Subtitle(start=1400, end=1900, text="2"),
        ]
    )

    output = get_stacked_series_from_groups(
        one, two, [([0], [0, 1])], timing_mode=timing_mode
    )

    assert [(event.start, event.end) for event in output.events] == expected_times
    assert [event.text for event in output.events] == ["A\\N1", "A\\N2"]


def test_get_stacked_series_overlap_error_includes_event_context():
    """Test impossible overlap removal errors include adjacent event context."""
    one = Series(
        events=[
            Subtitle(start=1000, end=3000, text="A"),
            Subtitle(start=1000, end=1001, text="B"),
        ]
    )

    with raises(
        ScinoephileError,
        match=("events 1 and 2.*previous=1000-3000.*current=1000-1001"),
    ):
        get_stacked_series_from_groups(one, Series(), [([0], []), ([1], [])])


@parametrize(
    ("one_fixture", "two_fixture", "expected_fixture"),
    [
        param(
            "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_eng_ocr_fuse_clean_validate_review_flatten",
            "acopopb_zho_hans_eng",
            id="acopopb-zho-hans-eng",
        ),
        param(
            "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acopopb_eng_ocr_fuse_clean_validate_review_flatten",
            "acopopb_yue_hans_eng",
            id="acopopb-yue-hans-eng",
        ),
        param(
            "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_eng_ocr_fuse_clean_validate_review_flatten",
            "acoptc_zho_hans_eng",
            id="acoptc-zho-hans-eng",
        ),
        param(
            "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "acoptc_eng_ocr_fuse_clean_validate_review_flatten",
            "acoptc_yue_hans_eng",
            id="acoptc-yue-hans-eng",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
            "kob_eng_ocr_fuse_clean_validate_review_flatten",
            "kob_zho_hans_eng",
            id="kob-zho-hans-eng",
        ),
        param(
            "kob_yue_hans_clean_review_flatten_timewarp",
            "kob_eng_clean_review_flatten_timewarp",
            "kob_yue_hans_eng",
            id="kob-yue-hans-eng",
        ),
        param(
            "mlamd_yue_hans_transcribe_review_translate_guided_review",
            "mlamd_eng_fuse_clean_validate_review_flatten",
            "mlamd_yue_hans_eng",
            id="mlamd-yue-hans-eng",
        ),
        param(
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            "mlamd_eng_fuse_clean_validate_review_flatten",
            "mlamd_zho_hans_eng",
            id="mlamd-zho-hans-eng",
        ),
        param(
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            "mnt_eng_fuse_clean_validate_review_flatten",
            "mnt_zho_hans_eng",
            id="mnt-zho-hans-eng",
        ),
        param(
            "t_zho_hans_fuse_clean_validate_review_flatten",
            "t_eng_fuse_clean_validate_review_flatten",
            "t_zho_hans_eng",
            id="t-zho-hans-eng",
        ),
        param(
            "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_eng_ocr_fuse_clean_validate_review_flatten",
            "tmm_zho_hans_eng",
            id="tmm-zho-hans-eng",
        ),
        param(
            "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten",
            "tmm_eng_ocr_fuse_clean_validate_review_flatten",
            "tmm_yue_hans_eng",
            id="tmm-yue-hans-eng",
        ),
    ],
)
def test_get_stacked_series(
    request: FixtureRequest,
    one_fixture: str,
    two_fixture: str,
    expected_fixture: str,
):
    """Test get_stacked_series against expected stacked outputs.

    Arguments:
        request: pytest request for fixture lookup
        one_fixture: fixture name for first input series
        two_fixture: fixture name for second input series
        expected_fixture: fixture name for expected output series
    """
    output = get_stacked_series(
        request.getfixturevalue(one_fixture),
        request.getfixturevalue(two_fixture),
    )
    assert_series_equal(output, request.getfixturevalue(expected_fixture))
