#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared transcription chunk recombination."""

from __future__ import annotations

import pytest

from scinoephile.audio.transcription import (
    TranscribedSegment,
    TranscribedWord,
    TranscriptionAlignmentError,
)
from scinoephile.audio.transcription.chunking import get_offset_core_segments


def test_get_offset_core_segments_skips_blank_untimed_segments():
    """Skip harmless blank segments while retaining timed chunk output."""
    blank_segment = TranscribedSegment(
        id=0, seek=0, start=0.0, end=0.0, text=" ", words=None
    )
    timed_segment = TranscribedSegment(
        id=1,
        seek=0,
        start=0.1,
        end=0.2,
        text="word",
        words=[TranscribedWord(text="word", start=0.1, end=0.2, confidence=1.0)],
    )

    segments = get_offset_core_segments(
        [blank_segment, timed_segment],
        offset_seconds=1.0,
        core_start_seconds=1.0,
        core_end_seconds=2.0,
        start_id=4,
    )

    assert len(segments) == 1
    assert segments[0].id == 4
    assert segments[0].text == "word"
    assert segments[0].start == pytest.approx(1.1)
    assert segments[0].end == pytest.approx(1.2)


def test_get_offset_core_segments_rejects_nonblank_untimed_segments():
    """Reject nonblank chunk output that cannot be assigned to a core window."""
    untimed_segment = TranscribedSegment(
        id=0, seek=0, start=0.0, end=0.1, text="word", words=None
    )

    with pytest.raises(TranscriptionAlignmentError, match="without word timings"):
        get_offset_core_segments(
            [untimed_segment],
            offset_seconds=0.0,
            core_start_seconds=0.0,
            core_end_seconds=1.0,
            start_id=0,
        )
