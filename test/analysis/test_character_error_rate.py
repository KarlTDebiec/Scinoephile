#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of character error rate analysis helpers."""

from __future__ import annotations

from math import inf

import pytest

from scinoephile.analysis import get_series_cer, get_text_cer
from scinoephile.core.subtitles import Series, Subtitle


def _get_series(*texts: str) -> Series:
    """Build a simple subtitle series for tests.

    Arguments:
        *texts: subtitle texts in order
    Returns:
        subtitle series
    """
    events = [
        Subtitle(start=index * 1000, end=(index + 1) * 1000, text=text)
        for index, text in enumerate(texts)
    ]
    return Series(events=events)


@pytest.mark.parametrize(
    ("reference", "hypothesis", "expected"),
    [
        (
            "abc",
            "abc",
            dict(
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
            dict(
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
            dict(
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
            dict(
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
            dict(
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
            dict(
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
            dict(
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
            dict(
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
            dict(
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
    hypothesis: str,
    expected: dict[str, float | int],
):
    """Test text-level character error rate calculations."""
    result = get_text_cer(reference, hypothesis)

    assert result.cer == expected["cer"]
    assert result.substitutions == expected["substitutions"]
    assert result.insertions == expected["insertions"]
    assert result.deletions == expected["deletions"]
    assert result.correct == expected["correct"]
    assert result.reference_length == expected["reference_length"]


def test_get_series_cer():
    """Test series-level character error rate calculations."""
    reference = _get_series("廣東", "話！")
    hypothesis = _get_series("廣 東", "话")

    result = get_series_cer(
        reference,
        hypothesis,
    )

    assert result.cer == 1 / 3
    assert result.substitutions == 1
    assert result.insertions == 0
    assert result.deletions == 0
    assert result.correct == 2
    assert result.reference_length == 3
