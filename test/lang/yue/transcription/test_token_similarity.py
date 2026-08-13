#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Yue-aware timed token similarity scoring."""

from __future__ import annotations

from scinoephile.analysis.alignment.timed_msa import Token
from scinoephile.lang.yue.transcription import YueTokenSimilarity


def test_yue_similarity_keeps_lexical_evidence_stronger_than_timing():
    """Recognized pronunciation should beat an unrelated same-time character."""
    similarity = YueTokenSimilarity(timing_weight=2.0, timing_tolerance_seconds=0.75)
    distant_pronunciation = similarity(Token("嗰", 0.0, 0.1), Token("個", 3.0, 3.1))
    unrelated_same_time = similarity(Token("嗰", 0.0, 0.1), Token("八", 0.0, 0.1))

    assert distant_pronunciation > unrelated_same_time


def test_yue_similarity_orders_substitution_evidence():
    """Test the substitution matrix ranks progressively weaker evidence."""
    similarity = YueTokenSimilarity(timing_weight=0.0)
    token = Token("係", 0.0, 0.1)

    exact = similarity(token, Token("係", 0.0, 0.1))
    compatibility_width = similarity(Token("J", 0.0, 0.1), Token("Ｊ", 0.0, 0.1))
    script = similarity(Token("裡", 0.0, 0.1), Token("里", 0.0, 0.1))
    equivalent = similarity(token, Token("是", 0.0, 0.1))
    same_jyutping = similarity(Token("事", 0.0, 0.1), Token("是", 0.0, 0.1))
    same_jyutping_base = similarity(Token("嗰", 0.0, 0.1), Token("個", 0.0, 0.1))
    unrelated = similarity(token, Token("八", 0.0, 0.1))

    assert compatibility_width == exact
    assert exact > script > equivalent
    assert equivalent > same_jyutping > same_jyutping_base > unrelated
