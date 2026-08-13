#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of timed alignment sequence creation."""

from __future__ import annotations

from pytest import raises

from scinoephile.analysis.alignment import timed_msa


def test_sequence_from_timed_texts_splits_units_and_omits_punctuation():
    """Test multi-character timing units become lexical character tokens."""
    sequence = timed_msa.Sequence.from_timed_texts("source", ((" 係呀！", 0.2, 0.6),))

    assert [token.text for token in sequence.tokens] == ["係", "呀"]
    assert [(token.start_seconds, token.end_seconds) for token in sequence.tokens] == [
        (0.2, 0.4),
        (0.4, 0.6),
    ]


def test_sequence_from_timed_texts_rejects_invalid_timing():
    """Timed text conversion should reject nonfinite and reversed intervals."""
    with raises(ValueError, match="finite"):
        timed_msa.Sequence.from_timed_texts("source", (("係", float("nan"), 0.6),))
    with raises(ValueError, match="must not precede"):
        timed_msa.Sequence.from_timed_texts("source", (("係", 0.6, 0.2),))
