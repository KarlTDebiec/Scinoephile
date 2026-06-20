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
        "source_one_fixture",
        "source_two_fixture",
        "expected_fixture",
        "one_end_idx",
        "two_end_idx",
    ),
    [
        param(
            "kob_eng_ocr_fuse_clean_validate_review",
            "kob_eng",
            "kob_eng_timewarp",
            1421,
            None,
            id="kob-eng",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            "kob_yue_hans",
            "kob_yue_hans_timewarp",
            1421,
            1461,
            id="kob-yue-hans",
        ),
        param(
            "kob_zho_hant_ocr_fuse_clean_validate_review",
            "kob_yue_hant",
            "kob_yue_hant_timewarp",
            1421,
            1461,
            id="kob-yue-hant",
        ),
    ],
)
def test_get_series_timewarped(
    request: FixtureRequest,
    source_one_fixture: str,
    source_two_fixture: str,
    expected_fixture: str,
    one_end_idx: int,
    two_end_idx: int | None,
):
    """Test get_series_timewarped with KOB subtitles.

    Arguments:
        request: pytest request for fixture lookup
        source_one_fixture: fixture name for anchor series
        source_two_fixture: fixture name for series to timewarp
        expected_fixture: fixture name for expected timewarped series
        one_end_idx: 1-based end index for the anchor series
        two_end_idx: optional 1-based end index for the timewarped series
    """
    output = get_series_timewarped(
        request.getfixturevalue(source_one_fixture),
        request.getfixturevalue(source_two_fixture),
        one_start_idx=1,
        one_end_idx=one_end_idx,
        two_start_idx=1,
        two_end_idx=two_end_idx,
    )
    expected: Series = request.getfixturevalue(expected_fixture)
    assert_series_equal(output, expected)
