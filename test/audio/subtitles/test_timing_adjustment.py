#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle timing adjustment."""

from __future__ import annotations

from pydub import AudioSegment

from scinoephile.audio.speech_activity import SpeechInterval
from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.audio.subtitles.timing_adjustment import (
    SubtitleTimingAdjustmentConfig,
    get_series_timing_adjusted,
    get_series_timing_adjustment,
)


class StaticSpeechDetector:
    """Speech detector returning configured intervals by block."""

    def __init__(self, blocks: list[list[SpeechInterval]]):
        """Initialize.

        Arguments:
            blocks: speech intervals to return for each detected block
        """
        self.blocks = list(blocks)

    def __call__(self, audio: AudioSegment) -> list[SpeechInterval]:
        """Return intervals for the next block.

        Arguments:
            audio: block audio
        Returns:
            speech intervals for the next block
        """
        return self.blocks.pop(0)


def test_get_series_timing_adjustment_expands_cue_and_reports_diagnostics():
    """Test a short cue expands to cover nearby speech."""
    series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[AudioSubtitle(start=1000, end=1500, text="hello")],
    )
    detector = StaticSpeechDetector([[SpeechInterval(start_ms=800, end_ms=2600)]])

    result = get_series_timing_adjustment(
        series,
        speech_detector=detector,
        config=SubtitleTimingAdjustmentConfig(
            max_start_expansion_ms=500,
            max_end_expansion_ms=1500,
        ),
    )

    adjusted = result.series
    assert [(event.start, event.end, event.text) for event in adjusted.events] == [
        (800, 2600, "hello")
    ]
    assert [(event.start, event.end) for event in series.events] == [(1000, 1500)]
    cue_diagnostics = result.cues[0]
    assert cue_diagnostics.speech_duration_ms == 1800
    assert cue_diagnostics.speech_coverage_before_ms == 500
    assert cue_diagnostics.speech_coverage_after_ms == 1800
    assert cue_diagnostics.start_delta_ms == -200
    assert cue_diagnostics.end_delta_ms == 1100
    assert cue_diagnostics.unchanged is False


def test_get_series_timing_adjustment_prevents_overlaps_and_reports_blocking():
    """Test end expansion is blocked by the next cue boundary."""
    series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[
            AudioSubtitle(start=1000, end=1500, text="one"),
            AudioSubtitle(start=1800, end=2300, text="two"),
        ],
    )
    detector = StaticSpeechDetector([[SpeechInterval(start_ms=1000, end_ms=1900)]])

    result = get_series_timing_adjustment(
        series,
        speech_detector=detector,
        config=SubtitleTimingAdjustmentConfig(
            max_start_expansion_ms=500,
            max_end_expansion_ms=1500,
        ),
    )

    assert [(event.start, event.end) for event in result.series.events] == [
        (1000, 1800),
        (1800, 2300),
    ]
    assert result.cues[0].blocked_end_expansion_ms == 100
    assert result.cues[1].unchanged is True


def test_get_series_timing_adjustment_applies_block_relative_offsets():
    """Test block-relative detector output is translated to series time."""
    series = AudioSeries(
        audio=AudioSegment.silent(duration=9000),
        events=[AudioSubtitle(start=5000, end=5500, text="offset")],
    )
    detector = StaticSpeechDetector([[SpeechInterval(start_ms=1400, end_ms=2400)]])

    adjusted = get_series_timing_adjusted(
        series,
        speech_detector=detector,
        config=SubtitleTimingAdjustmentConfig(
            block_audio_buffer_ms=1500,
            max_start_expansion_ms=500,
            max_end_expansion_ms=500,
        ),
    )

    assert [(event.start, event.end) for event in adjusted.events] == [(4900, 5900)]


def test_get_series_timing_adjustment_preserves_middle_of_complex_sync_group():
    """Test complex sync groups adjust outer edges without moving middle timings."""
    series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[
            AudioSubtitle(start=1000, end=1400, text="one"),
            AudioSubtitle(start=1700, end=2100, text="two"),
        ],
    )
    detector = StaticSpeechDetector([[SpeechInterval(start_ms=700, end_ms=2600)]])

    result = get_series_timing_adjustment(
        series,
        speech_detector=detector,
        config=SubtitleTimingAdjustmentConfig(
            max_start_expansion_ms=500,
            max_end_expansion_ms=800,
        ),
    )

    assert [(event.start, event.end) for event in result.series.events] == [
        (700, 1400),
        (1700, 2600),
    ]
    assert result.cues[0].start_delta_ms == -300
    assert result.cues[0].end_delta_ms == 0
    assert result.cues[1].start_delta_ms == 0
    assert result.cues[1].end_delta_ms == 500


def test_get_series_timing_adjustment_leaves_empty_speech_blocks_unchanged():
    """Test blocks with no detected speech keep original cue timings."""
    series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[AudioSubtitle(start=1000, end=1500, text="quiet")],
    )

    result = get_series_timing_adjustment(
        series,
        speech_detector=StaticSpeechDetector([[]]),
    )

    assert [(event.start, event.end) for event in result.series.events] == [
        (1000, 1500)
    ]
    assert result.cues[0].unchanged is True
