#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of character error rate analysis helpers."""

from __future__ import annotations

from math import inf

import pytest

from scinoephile.analysis.character_error_rate import LineCER, SeriesCER
from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import SeriesCERResult


def _get_series(*texts: str) -> Series:
    """Build a compact subtitle series for CER tests.

    Arguments:
        *texts: subtitle event texts
    Returns:
        subtitle series with one event per text
    """
    return Series(
        events=[
            Subtitle(start=idx * 1000, end=idx * 1000 + 500, text=text)
            for idx, text in enumerate(texts)
        ]
    )


@pytest.mark.parametrize(
    ("reference", "candidate", "expected"),
    [
        (
            "abc",
            "abc",
            SeriesCERResult(
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
            SeriesCERResult(
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
            SeriesCERResult(
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
            SeriesCERResult(
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
            SeriesCERResult(
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
            SeriesCERResult(
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
            SeriesCERResult(
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
            SeriesCERResult(
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
            SeriesCERResult(
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
def test_line_cer(
    reference: str,
    candidate: str,
    expected: SeriesCERResult,
):
    """Test line-level character error rate calculations.

    Arguments:
        reference: reference text
        candidate: candidate text
        expected: expected CER result
    """
    result = LineCER(reference, candidate)

    assert result.cer == expected.cer
    assert result.substitutions == expected.substitutions
    assert result.insertions == expected.insertions
    assert result.deletions == expected.deletions
    assert result.correct == expected.correct
    assert result.reference_length == expected.reference_length


@pytest.mark.parametrize(
    ("reference", "candidate"),
    [
        (_get_series("你", "好"), _get_series("你好")),
        (_get_series("ab"), _get_series("a", "b")),
    ],
)
def test_series_cer_ignores_separator_only_line_wrapping(
    reference: Series,
    candidate: Series,
):
    """Test separator-only line wrapping does not affect series CER."""
    result = SeriesCER(reference, candidate)

    assert result.cer == 0.0
    assert result.substitutions == 0
    assert result.insertions == 0
    assert result.deletions == 0


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
            "kob_yue_hans_transcribe_review_translate_block_review",
            "kob_yue_hans_transcribe_review_translate_block_review_expected_cer",
        ),
    ],
)
def test_series_cer(
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
    expected: SeriesCERResult = request.getfixturevalue(expected_fixture_name)

    result = SeriesCER(reference_series, candidate_series)

    assert result.cer == expected.cer
    assert result.substitutions == expected.substitutions
    assert result.insertions == expected.insertions
    assert result.deletions == expected.deletions
    assert result.correct == expected.correct
    assert result.reference_length == expected.reference_length
