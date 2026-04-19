#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of character error rate analysis helpers."""

from __future__ import annotations

from math import inf

import pytest

from scinoephile.analysis import CharacterErrorRateResult, get_series_cer, get_text_cer
from scinoephile.core.subtitles import Series


@pytest.mark.parametrize(
    ("reference", "candidate", "expected"),
    [
        (
            "abc",
            "abc",
            CharacterErrorRateResult(
                cer=0.0,
                substitutions=0,
                insertions=0,
                deletions=0,
                correct=3,
                reference_length=3,
            ),
        ),
        (
            "abc",
            "axc",
            CharacterErrorRateResult(
                cer=1 / 3,
                substitutions=1,
                insertions=0,
                deletions=0,
                correct=2,
                reference_length=3,
            ),
        ),
        (
            "abc",
            "abxc",
            CharacterErrorRateResult(
                cer=1 / 3,
                substitutions=0,
                insertions=1,
                deletions=0,
                correct=3,
                reference_length=3,
            ),
        ),
        (
            "abc",
            "ac",
            CharacterErrorRateResult(
                cer=1 / 3,
                substitutions=0,
                insertions=0,
                deletions=1,
                correct=2,
                reference_length=3,
            ),
        ),
        (
            "a b",
            "ab",
            CharacterErrorRateResult(
                cer=0.0,
                substitutions=0,
                insertions=0,
                deletions=0,
                correct=2,
                reference_length=2,
            ),
        ),
        (
            "a,b!",
            "ab",
            CharacterErrorRateResult(
                cer=0.0,
                substitutions=0,
                insertions=0,
                deletions=0,
                correct=2,
                reference_length=2,
            ),
        ),
        (
            "廣東話",
            "广东话",
            CharacterErrorRateResult(
                cer=1.0,
                substitutions=3,
                insertions=0,
                deletions=0,
                correct=0,
                reference_length=3,
            ),
        ),
        (
            "",
            "",
            CharacterErrorRateResult(
                cer=0.0,
                substitutions=0,
                insertions=0,
                deletions=0,
                correct=0,
                reference_length=0,
            ),
        ),
        (
            "",
            "abc",
            CharacterErrorRateResult(
                cer=inf,
                substitutions=0,
                insertions=3,
                deletions=0,
                correct=0,
                reference_length=0,
            ),
        ),
    ],
)
def test_get_text_cer(
    reference: str,
    candidate: str,
    expected: CharacterErrorRateResult,
):
    """Test text-level character error rate calculations.

    Arguments:
        reference: reference text
        candidate: candidate text
        expected: expected CER result
    """
    result = get_text_cer(reference, candidate)

    assert result == expected


@pytest.mark.parametrize(
    (
        "reference_series_fixture_name",
        "candidate_series_fixture_name",
        "expected_fixture_name",
    ),
    [
        (
            "kob_yue_hans_timewarp_clean_flatten",
            "kob_yue_hans_transcribe",
            "kob_yue_hans_transcribe_expected_cer",
        ),
        (
            "kob_yue_hans_timewarp_clean_flatten",
            "kob_yue_hans_transcribe_proofread_translate_review",
            "kob_yue_hans_transcribe_proofread_translate_review_expected_cer",
        ),
    ],
)
def test_get_series_cer(
    reference_series_fixture_name: str,
    candidate_series_fixture_name: str,
    expected_fixture_name: str,
    request: pytest.FixtureRequest,
):
    """Test series-level character error rate calculations.

    Arguments:
        reference_series_fixture_name: fixture name for reference subtitle series
        candidate_series_fixture_name: fixture name for candidate subtitle series
        expected_fixture_name: fixture name containing expected CER result
        request: pytest fixture request object
    """
    reference_series: Series = request.getfixturevalue(reference_series_fixture_name)
    candidate_series: Series = request.getfixturevalue(candidate_series_fixture_name)
    expected: CharacterErrorRateResult = request.getfixturevalue(expected_fixture_name)

    result = get_series_cer(reference_series, candidate_series)

    assert result == expected
