#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of transcription reference alignment sequences."""

from __future__ import annotations

from scinoephile.analysis.transcription.alignment_sequence import get_reference_sequence
from scinoephile.core.subtitles import Series, Subtitle


def test_get_reference_sequence_applies_source_offset():
    """Test subtitle reference characters receive alignment-local timings."""
    reference = Series(
        events=[
            Subtitle(start=8_000, end=9_000, text="之前"),
            Subtitle(start=10_000, end=12_000, text="这是！"),
        ]
    )

    sequence = get_reference_sequence("reference", reference, offset_seconds=10.0)

    assert [token.text for token in sequence.tokens] == ["这", "是"]
    assert [(token.start_seconds, token.end_seconds) for token in sequence.tokens] == [
        (0.0, 1.0),
        (1.0, 2.0),
    ]
