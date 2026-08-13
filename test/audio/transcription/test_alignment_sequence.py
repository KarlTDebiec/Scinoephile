#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of transcription alignment sequence construction."""

from __future__ import annotations

from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.audio.transcription.alignment_sequence import (
    get_transcription_sequence,
)


def test_get_transcription_sequence_uses_word_timings():
    """Test ASR word timings become approximate lexical character timings."""
    segments = [
        TranscribedSegment(
            id=0,
            seek=0,
            start=0.0,
            end=1.0,
            text=" 係呀！",
            words=[TranscribedWord(text=" 係呀！", start=0.2, end=0.6, confidence=0.9)],
        )
    ]

    sequence = get_transcription_sequence("whisper", segments)

    assert [token.text for token in sequence.tokens] == ["係", "呀"]
    assert [(token.start_seconds, token.end_seconds) for token in sequence.tokens] == [
        (0.2, 0.4),
        (0.4, 0.6),
    ]
