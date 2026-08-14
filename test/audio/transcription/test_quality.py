#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for timestamped transcription quality validation."""

from __future__ import annotations

from pytest import mark

from scinoephile.audio.transcription.quality import get_transcription_quality_issue
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord


@mark.parametrize(
    ("start", "end", "has_issue"), ((0.1004, 0.1006, False), (0.1006, 0.1014, True))
)
def test_quality_uses_rounded_millisecond_duration(
    start: float, end: float, has_issue: bool
):
    """Quality should match the millisecond quantization used by subtitles.

    Arguments:
        start: segment and word start in seconds
        end: segment and word end in seconds
        has_issue: whether rounded bounds have non-positive duration
    """
    word = TranscribedWord(text="word", start=start, end=end, confidence=1.0)
    segment = TranscribedSegment(
        id=0, seek=0, start=start, end=end, text="word", words=[word]
    )

    issue = get_transcription_quality_issue([segment])

    assert (issue is not None) is has_issue
