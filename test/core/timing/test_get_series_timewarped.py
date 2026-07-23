#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.timing.get_series_timewarped."""

from __future__ import annotations

from pytest import FixtureRequest, param, raises

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.core.timing import get_series_timewarped
from test.helpers import assert_series_equal, parametrize


@parametrize(
    (
        "reference_fixture_name",
        "series_fixture_name",
        "expected_fixture_name",
        "one_end_idx",
        "two_end_idx",
    ),
    [
        param(
            "kob_eng_ocr_fuse_clean_validate_review",
            "kob_eng_clean_review_flatten",
            "kob_eng_clean_review_flatten_timewarp",
            1421,
            None,
            id="kob-eng-srt",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            "kob_yue_hans_clean_review_flatten",
            "kob_yue_hans_clean_review_flatten_timewarp",
            1421,
            1461,
            id="kob-yue-hans-srt",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            "kob_yue_hant_clean_review_flatten",
            "kob_yue_hant_clean_review_flatten_timewarp",
            1421,
            1461,
            id="kob-yue-hant-srt",
        ),
    ],
)
def test_get_series_timewarped(
    request: FixtureRequest,
    reference_fixture_name: str,
    series_fixture_name: str,
    expected_fixture_name: str,
    one_end_idx: int,
    two_end_idx: int | None,
):
    """Test get_series_timewarped with KOB subtitles.

    Arguments:
        request: pytest request object
        reference_fixture_name: fixture name for anchor subtitles
        series_fixture_name: fixture name for source subtitles
        expected_fixture_name: fixture name for expected timewarped subtitles
        one_end_idx: 1-based end index in the anchor series
        two_end_idx: 1-based end index in the source series
    """
    reference: Series = request.getfixturevalue(reference_fixture_name)
    series: Series = request.getfixturevalue(series_fixture_name)
    expected: Series = request.getfixturevalue(expected_fixture_name)
    output = get_series_timewarped(
        reference,
        series,
        one_start_idx=1,
        one_end_idx=one_end_idx,
        two_start_idx=1,
        two_end_idx=two_end_idx,
    )
    assert_series_equal(output, expected)


@parametrize(
    "kwargs, label",
    [
        param({"one_start_idx": 0}, "source one start", id="source-one-start"),
        param({"one_end_idx": 0}, "source one end", id="source-one-end"),
        param({"two_start_idx": 0}, "source two start", id="source-two-start"),
        param({"two_end_idx": 0}, "source two end", id="source-two-end"),
    ],
)
def test_get_series_timewarped_rejects_zero_indexes(
    kwargs: dict[str, int],
    label: str,
):
    """Test explicit zero indexes are rejected instead of defaulted.

    Arguments:
        kwargs: timewarp index override
        label: expected index label in the error message
    """
    source_one = _get_series()
    source_two = _get_series()

    with raises(
        ScinoephileError,
        match=f"Invalid {label} index 0",
    ):
        get_series_timewarped(source_one, source_two, **kwargs)


@parametrize(
    "kwargs, label",
    [
        param(
            {"one_start_idx": 2, "one_end_idx": 1},
            "source one",
            id="source-one",
        ),
        param(
            {"two_start_idx": 2, "two_end_idx": 1},
            "source two",
            id="source-two",
        ),
    ],
)
def test_get_series_timewarped_rejects_reversed_ranges(
    kwargs: dict[str, int],
    label: str,
):
    """Test timewarp anchor ranges must be ordered from start to end.

    Arguments:
        kwargs: timewarp index overrides
        label: expected range label in the error message
    """
    source_one = _get_series()
    source_two = _get_series()

    with raises(
        ScinoephileError,
        match=f"Invalid {label} range 2-1",
    ):
        get_series_timewarped(source_one, source_two, **kwargs)


def _get_series() -> Series:
    """Get a small series for timewarp validation tests."""
    return Series(
        events=[
            Subtitle(start=0, end=1000, text="First"),
            Subtitle(start=2000, end=3000, text="Second"),
        ]
    )
