#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.timing.get_series_timewarped."""

from __future__ import annotations

from pytest import FixtureRequest, param

from scinoephile.core.subtitles import Series
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
def test_get_series_timewarped_kob(
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
