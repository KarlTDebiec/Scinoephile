#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Yue-aware timed token similarity scoring."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.alignment.timed_msa import MsaToken
from scinoephile.lang.yue.transcription import YueTokenSimilarity


def test_yue_similarity_keeps_lexical_evidence_stronger_than_timing():
    """Recognized pronunciation should beat an unrelated same-time character."""
    similarity = YueTokenSimilarity(timing_weight=2.0, timing_tolerance_seconds=0.75)
    distant_pronunciation = similarity(
        MsaToken("嗰", 0.0, 0.1), MsaToken("個", 3.0, 3.1)
    )
    unrelated_same_time = similarity(MsaToken("嗰", 0.0, 0.1), MsaToken("八", 0.0, 0.1))

    assert distant_pronunciation > unrelated_same_time


def test_yue_similarity_rejects_nonfinite_configuration():
    """Non-finite settings should fail before they contaminate alignment scores."""
    with raises(ValueError, match="lexical scores must be finite"):
        YueTokenSimilarity(exact_score=float("nan"))
    with raises(ValueError, match="timing weight must be finite"):
        YueTokenSimilarity(timing_weight=float("nan"))
    with raises(ValueError, match="timing tolerance must be finite"):
        YueTokenSimilarity(timing_tolerance_seconds=float("inf"))


def test_yue_similarity_orders_substitution_evidence():
    """Test the substitution matrix ranks progressively weaker evidence."""
    similarity = YueTokenSimilarity(timing_weight=0.0)
    token = MsaToken("係", 0.0, 0.1)

    exact = similarity(token, MsaToken("係", 0.0, 0.1))
    compatibility_width = similarity(MsaToken("J", 0.0, 0.1), MsaToken("Ｊ", 0.0, 0.1))
    script = similarity(MsaToken("裡", 0.0, 0.1), MsaToken("里", 0.0, 0.1))
    equivalent = similarity(token, MsaToken("是", 0.0, 0.1))
    same_jyutping = similarity(MsaToken("事", 0.0, 0.1), MsaToken("是", 0.0, 0.1))
    same_jyutping_base = similarity(MsaToken("嗰", 0.0, 0.1), MsaToken("個", 0.0, 0.1))
    unrelated = similarity(token, MsaToken("八", 0.0, 0.1))

    assert compatibility_width == exact
    assert exact > script > equivalent
    assert equivalent > same_jyutping > same_jyutping_base > unrelated
