#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.test_get_eng_flattened."""

from __future__ import annotations

import pytest

# noinspection PyProtectedMember
from scinoephile.lang.eng.flattening import _get_eng_text_flattened, get_eng_flattened
from test.helpers import assert_series_equal


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture"),
    [
        (
            "kob_eng_ocr_fuse_clean_validate_review",
            "kob_eng_ocr_fuse_clean_validate_review_flatten",
        ),
        (
            "mlamd_eng_fuse_clean_validate_review",
            "mlamd_eng_fuse_clean_validate_review_flatten",
        ),
        (
            "mnt_eng_fuse_clean_validate_review",
            "mnt_eng_fuse_clean_validate_review_flatten",
        ),
        (
            "t_eng_fuse_clean_validate_review",
            "t_eng_fuse_clean_validate_review_flatten",
        ),
    ],
)
def test_get_eng_flattened(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_eng_flattened against expected flattened outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: fixture name for input series
        expected_fixture: fixture name for expected output series
    """
    series = request.getfixturevalue(series_fixture)
    output = get_eng_flattened(series)

    assert len(series) == len(output)

    errors = []
    for i, event in enumerate(output, 1):
        if event.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")
    assert_series_equal(output, request.getfixturevalue(expected_fixture))


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1 line 2"),
    ],
)
def test_get_eng_text_flattened(text: str, expected: str):
    """Test get_eng_text_flattened.

    Arguments:
        text: Text to flatten
        expected: Expected flattened text
    """
    assert _get_eng_text_flattened(text) == expected
