#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of `SeriesDiff`."""

from __future__ import annotations

import pytest

from scinoephile.analysis import SeriesDiff
from scinoephile.core.subtitles import Series


def _assert_expected_differences(differences: SeriesDiff, expected: list[str]):
    """Assert that expected differences are present.

    Arguments:
        differences: series diff to check
        expected: list of expected difference strings
    """
    formatted_differences = [str(diff) for diff in differences]
    missing = [diff for diff in expected if diff not in formatted_differences]
    if missing:
        formatted = "\n".join(missing)
        raise AssertionError(f"Missing expected differences:\n{formatted}")


@pytest.mark.parametrize(
    (
        "one_series_fixture_name",
        "two_series_fixture_name",
        "one_lbl",
        "two_lbl",
        "expected_fixture_name",
    ),
    [
        (
            "kob_eng_ocr_fuse_clean_validate_review_flatten",
            "kob_eng_timewarp_clean_review_flatten",
            "OCR",
            "SRT",
            "kob_eng_expected_series_diff",
        ),
        (
            "mlamd_zho_hans_fuse_clean_validate_review_flatten",
            "mlamd_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "mlamd_zho_simplify_expected_series_diff",
        ),
        (
            "mnt_zho_hans_fuse_clean_validate_review_flatten",
            "mnt_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "mnt_zho_simplify_expected_series_diff",
        ),
        (
            "t_zho_hans_fuse_clean_validate_review_flatten",
            "t_zho_hant_fuse_clean_validate_review_flatten_simplify_review",
            "SIMP",
            "TRAD",
            "t_zho_simplify_expected_series_diff",
        ),
    ],
)
def test_series_diff(
    one_series_fixture_name: str,
    two_series_fixture_name: str,
    one_lbl: str,
    two_lbl: str,
    expected_fixture_name: str,
    request: pytest.FixtureRequest,
):
    """Test `SeriesDiff` for subtitle fixture pairs.

    Arguments:
        one_series_fixture_name: fixture name for first subtitle series
        two_series_fixture_name: fixture name for second subtitle series
        one_lbl: label for first subtitle stream in diff output
        two_lbl: label for second subtitle stream in diff output
        expected_fixture_name: fixture name containing expected diff strings
        request: pytest fixture request object
    """
    one_series: Series = request.getfixturevalue(one_series_fixture_name)
    two_series: Series = request.getfixturevalue(two_series_fixture_name)
    expected: list[str] = request.getfixturevalue(expected_fixture_name)

    differences = SeriesDiff(
        one_series,
        two_series,
        one_lbl=one_lbl,
        two_lbl=two_lbl,
    )
    _assert_expected_differences(differences, expected)
