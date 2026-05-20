#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of speech activity helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pydub import AudioSegment

from scinoephile.audio.speech_activity import (
    SileroSpeechActivityDetector,
    SpeechInterval,
    WhisperSpeechActivityDetector,
    get_speech_intervals_cleaned,
    get_speech_intervals_from_segments,
    get_speech_series_from_intervals,
)
from scinoephile.audio.transcription import TranscribedSegment


class StubTranscriber:
    """Stub speech transcriber."""

    def __init__(self, segments: list[TranscribedSegment]):
        """Initialize.

        Arguments:
            segments: segments to return
        """
        self.segments = segments

    def __call__(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Return configured segments.

        Arguments:
            audio: ignored audio segment
        Returns:
            configured transcription segments
        """
        return self.segments


def test_speech_interval_shift_and_clip():
    """Test intervals can be shifted and clipped."""
    interval = SpeechInterval(start_ms=100, end_ms=300)

    assert interval.duration_ms == 200
    assert interval.shifted(50) == SpeechInterval(start_ms=150, end_ms=350)
    assert interval.clipped(start_ms=150, end_ms=250) == SpeechInterval(
        start_ms=150,
        end_ms=250,
    )
    assert interval.clipped(start_ms=300, end_ms=400) is None


def test_get_speech_intervals_cleaned_merges_discards_and_clips():
    """Test interval cleanup merges gaps, discards short islands, and clips bounds."""
    intervals = [
        SpeechInterval(start_ms=100, end_ms=180),
        SpeechInterval(start_ms=200, end_ms=260),
        SpeechInterval(start_ms=400, end_ms=900),
        SpeechInterval(start_ms=930, end_ms=1200),
    ]

    cleaned = get_speech_intervals_cleaned(
        intervals,
        merge_gap_ms=50,
        min_duration_ms=100,
        clip_start_ms=250,
        clip_end_ms=1000,
    )

    assert cleaned == [SpeechInterval(start_ms=400, end_ms=1000)]


def test_get_speech_intervals_from_segments_applies_offset():
    """Test transcription segments are normalized to millisecond intervals."""
    segments = [
        TranscribedSegment(id=0, seek=0, start=0.125, end=0.5, text="hello"),
        TranscribedSegment(id=1, seek=0, start=0.55, end=0.9, text="again"),
    ]

    intervals = get_speech_intervals_from_segments(segments, offset_ms=1000)

    assert intervals == [
        SpeechInterval(start_ms=1125, end_ms=1500),
        SpeechInterval(start_ms=1550, end_ms=1900),
    ]


def test_get_speech_series_from_intervals_uses_empty_text_events():
    """Test speech intervals can be represented as an empty subtitle series."""
    intervals = [
        SpeechInterval(start_ms=1000, end_ms=1500),
        SpeechInterval(start_ms=2000, end_ms=2600),
    ]

    series = get_speech_series_from_intervals(intervals)

    assert [(event.start, event.end, event.text) for event in series.events] == [
        (1000, 1500, ""),
        (2000, 2600, ""),
    ]


def test_whisper_speech_activity_detector_cleans_transcription_segments():
    """Test Whisper-backed detection delegates and cleans segment timings."""
    segments = [
        TranscribedSegment(id=0, seek=0, start=0.1, end=0.5, text="hello"),
        TranscribedSegment(id=1, seek=0, start=0.55, end=1.0, text="again"),
        TranscribedSegment(id=2, seek=0, start=1.5, end=1.55, text="x"),
    ]
    detector = WhisperSpeechActivityDetector(
        transcriber=StubTranscriber(segments),
        merge_gap_ms=100,
        min_duration_ms=100,
    )

    intervals = detector(AudioSegment.silent(duration=2000), offset_ms=3000)

    assert intervals == [SpeechInterval(start_ms=3100, end_ms=4000)]


def test_silero_speech_activity_detector_caches_and_cleans_timestamps(tmp_path: Path):
    """Test Silero-backed detection caches raw intervals before cleanup."""
    cache_dir_path = tmp_path / "speech"
    audio = AudioSegment.silent(duration=2000)

    with patch.object(
        SileroSpeechActivityDetector,
        "_get_uncached_speech_intervals",
        return_value=[
            SpeechInterval(start_ms=100, end_ms=500),
            SpeechInterval(start_ms=550, end_ms=1000),
            SpeechInterval(start_ms=1500, end_ms=1550),
        ],
    ) as get_uncached_speech_intervals:
        detector = SileroSpeechActivityDetector(
            model=object(),
            cache_dir_path=cache_dir_path,
            merge_gap_ms=100,
            min_duration_ms=100,
        )

        intervals = detector(audio, offset_ms=3000)

    assert intervals == [SpeechInterval(start_ms=3100, end_ms=4000)]
    get_uncached_speech_intervals.assert_called_once_with(audio)

    with patch.object(
        SileroSpeechActivityDetector,
        "_get_uncached_speech_intervals",
        side_effect=AssertionError("cache miss"),
    ):
        cached_detector = SileroSpeechActivityDetector(
            model=object(),
            cache_dir_path=cache_dir_path,
            merge_gap_ms=100,
            min_duration_ms=100,
        )

        cached_intervals = cached_detector(audio, offset_ms=3000)

    assert cached_intervals == [SpeechInterval(start_ms=3100, end_ms=4000)]


def test_whisper_speech_activity_detector_uses_cached_transcriber(tmp_path: Path):
    """Test Whisper-backed detection can cache raw transcription segments."""
    cache_dir_path = tmp_path / "speech"

    with patch(
        "scinoephile.audio.speech_activity.WhisperTranscriber"
    ) as transcriber_cls:
        detector = WhisperSpeechActivityDetector(cache_dir_path=cache_dir_path)

    transcriber_cls.assert_called_once_with(cache_dir_path=cache_dir_path)
    assert detector.transcriber == transcriber_cls.return_value
