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


def test_get_series_cer_kob_transcribe(
    kob_yue_hans_timewarp_clean_flatten: Series,
    kob_yue_hans_transcribe: Series,
):
    """Test KOB CER for transcribed subtitles against the flattened reference.

    Arguments:
        kob_yue_hans_timewarp_clean_flatten: reference subtitles
        kob_yue_hans_transcribe: transcribed subtitles
    """
    result = get_series_cer(
        kob_yue_hans_timewarp_clean_flatten,
        kob_yue_hans_transcribe,
    )

    assert result == CharacterErrorRateResult(
        cer=0.9040239499867923,
        substitutions=4155,
        insertions=2835,
        deletions=3277,
        correct=3925,
        reference_length=11357,
    )


def test_get_series_cer_kob_transcribe_proofread_translate_review(
    kob_yue_hans_timewarp_clean_flatten: Series,
    kob_yue_hans_transcribe_proofread_translate_review: Series,
):
    """Test KOB CER after proofread/translate/review against the reference.

    Arguments:
        kob_yue_hans_timewarp_clean_flatten: reference subtitles
        kob_yue_hans_transcribe_proofread_translate_review: reviewed subtitles
    """
    result = get_series_cer(
        kob_yue_hans_timewarp_clean_flatten,
        kob_yue_hans_transcribe_proofread_translate_review,
    )

    assert result == CharacterErrorRateResult(
        cer=0.6034163951747821,
        substitutions=2789,
        insertions=2091,
        deletions=1973,
        correct=6595,
        reference_length=11357,
    )
