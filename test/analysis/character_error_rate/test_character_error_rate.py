#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of character error rate analysis helpers."""

from __future__ import annotations

from math import inf

from scinoephile.analysis.character_error_rate import LineCER, SeriesCER
from scinoephile.core.subtitles import Series
from test.helpers import SeriesCERResult, parametrize
from test.helpers.series_files import get_text_series


@parametrize(
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
def test_line_cer(reference: str, candidate: str, expected: SeriesCERResult):
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


def test_line_cer_string_includes_percentages():
    """Test line-level CER output includes percentages of reference length."""
    result = LineCER("abc", "axc")

    assert str(result) == (
        "CER: 0.3333333333333333\n"
        "Correct: 2 (66.67%)\n"
        "Substitutions: 1 (33.33%)\n"
        "Insertions: 0 (0.00%)\n"
        "Deletions: 0 (0.00%)\n"
        "Reference length: 3"
    )


def test_line_cer_string_uses_na_for_empty_reference():
    """Test line-level CER component percentages require a reference."""
    result = LineCER("", "abc")

    assert str(result) == (
        "CER: inf\n"
        "Correct: 0 (N/A)\n"
        "Substitutions: 0 (N/A)\n"
        "Insertions: 3 (N/A)\n"
        "Deletions: 0 (N/A)\n"
        "Reference length: 0"
    )


@parametrize(
    ("reference", "candidate"),
    [
        (get_text_series("你", "好"), get_text_series("你好")),
        (get_text_series("ab"), get_text_series("a", "b")),
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


def test_series_cer_string_includes_percentages():
    """Test series-level CER output includes percentages of reference length."""
    result = SeriesCER(get_text_series("abc"), get_text_series("axc"))

    assert str(result) == (
        "CER: 0.3333333333333333\n"
        "Correct: 2 (66.67%)\n"
        "Substitutions: 1 (33.33%)\n"
        "Insertions: 0 (0.00%)\n"
        "Deletions: 0 (0.00%)\n"
        "Reference length: 3"
    )


def test_series_cer_string_uses_na_for_empty_reference():
    """Test series-level CER component percentages require a reference."""
    result = SeriesCER(get_text_series(), get_text_series("abc"))

    assert str(result) == (
        "CER: inf\n"
        "Correct: 0 (N/A)\n"
        "Substitutions: 0 (N/A)\n"
        "Insertions: 3 (N/A)\n"
        "Deletions: 0 (N/A)\n"
        "Reference length: 0"
    )
