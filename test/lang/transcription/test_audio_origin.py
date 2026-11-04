#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio-origin regressions for transcription conversion, splitting, and alignment."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, patch

from pydub import AudioSegment
from pydub.generators import Sine
from pytest import raises

from scinoephile.audio.subtitles import (
    AudioSeries,
    AudioSubtitle,
    get_series_from_segments,
    get_series_with_sub_split_at_idx,
)
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.audio.transcription.whisper import WhisperModelSpec
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.aligner import TranscriptionAligner
from scinoephile.lang.transcription.transcriber import GuidedTranscriber
from test.helpers import parametrize


@parametrize(
    ("audio_start_ms", "exception_class"),
    [(-1, ValueError), (True, TypeError), (0.5, TypeError), ("10000", TypeError)],
)
def test_audio_origin_constructor_rejects_invalid_values(
    audio_start_ms: object, exception_class: type[Exception]
):
    """Require an explicit origin to be a nonnegative integer timestamp.

    Arguments:
        audio_start_ms: invalid audio-origin value
        exception_class: expected validation exception
    """
    with raises(exception_class):
        AudioSeries(
            audio=AudioSegment.silent(duration=1000),
            audio_start_ms=cast(int, audio_start_ms),
        )


def test_audio_origin_defaults_to_zero_for_existing_constructor_calls():
    """Preserve the original positional constructor and zero-origin default."""
    audio = AudioSegment.silent(duration=1000)
    assert AudioSeries(audio, []).audio_start_ms == 0


@parametrize("buffered", [False, True])
def test_guided_process_block_preserves_audio_origin_through_alignment(buffered: bool):
    """Retain exact nonempty audio with explicit buffers and origin-based fallback.

    Arguments:
        buffered: whether the input includes explicit buffered timing metadata
    """
    audio = Sine(440).to_audio_segment(duration=3000)
    audio_block = AudioSeries(
        audio=audio,
        events=[AudioSubtitle(start=10500, end=11500, text="Cue")],
        audio_start_ms=10000,
    )
    if buffered:
        audio_block.buffered_start = 10000
    reference = Series(events=[Subtitle(start=10500, end=11500, text="Cue")])
    aligner = TranscriptionAligner(Mock(), Mock())
    transcriber = _get_transcriber(aligner)
    segment = TranscribedSegment(id=0, seek=0, start=0.5, end=1.5, text="Cue")

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        output = transcriber.process_block(audio_block, reference)

    assert output.audio_start_ms == 10000
    assert [(event.start, event.end) for event in output] == [(10500, 11500)]
    assert output.slice(0, 1).audio.raw_data == audio[500:1500].raw_data
    assert output.slice(0, 1).slice(0, 1).audio.raw_data == audio[500:1500].raw_data
    assert output.blocks[0].audio.raw_data == audio[:2500].raw_data
    assert output.blocks[0].slice(0, 1).audio.raw_data == audio[500:1500].raw_data


def test_guided_process_preserves_origin_when_recombining_output_blocks():
    """The guided series result retains the source audio's timestamp mapping."""
    audio = Sine(440).to_audio_segment(duration=3000)
    series = AudioSeries(
        audio=audio,
        events=[AudioSubtitle(start=10500, end=11500, text="Cue")],
        audio_start_ms=10000,
    )
    reference = Series(events=[Subtitle(start=10500, end=11500, text="Cue")])
    aligner = TranscriptionAligner(Mock(), Mock())
    transcriber = _get_transcriber(aligner)
    segment = TranscribedSegment(id=0, seek=0, start=0.5, end=1.5, text="Cue")

    with patch.object(transcriber, "_transcribe_block_audio", return_value=[segment]):
        output = transcriber.process(series, reference)

    assert output.audio_start_ms == 10000
    assert output.audio.raw_data == audio.raw_data
    assert output.slice(0, 1).audio.raw_data == audio[500:1500].raw_data


def test_segment_conversion_and_split_alignment_preserve_origin():
    """Keep audio aligned after converting local segments and splitting their cues."""
    audio = Sine(440).to_audio_segment(duration=3000)
    segment = TranscribedSegment(
        id=0,
        seek=0,
        start=0.5,
        end=1.5,
        text="AB",
        words=[
            TranscribedWord(text="A", start=0.5, end=1.0, confidence=1),
            TranscribedWord(text="B", start=1.0, end=1.5, confidence=1),
        ],
    )
    series = get_series_from_segments([segment], audio=audio, offset=10000)
    split = get_series_with_sub_split_at_idx(series, 0, 1)
    reference = Series(
        events=[
            Subtitle(start=10500, end=11000, text="A"),
            Subtitle(start=11000, end=11500, text="B"),
        ]
    )
    aligner = TranscriptionAligner(Mock(), Mock())
    with patch.object(aligner, "_delineate", return_value=False):
        aligned = aligner.align(reference, split).transcription

    for output in (series, split, aligned):
        assert output.audio_start_ms == 10000
        assert output.slice(0, len(output)).audio.raw_data == audio[500:1500].raw_data
        assert output.blocks[0].audio.raw_data == audio[:2500].raw_data
    assert split.slice(1, 2).audio.raw_data == audio[1000:1500].raw_data
    assert aligned.slice(1, 2).audio.raw_data == audio[1000:1500].raw_data


def _get_transcriber(aligner: TranscriptionAligner) -> GuidedTranscriber:
    """Create a lazy model wrapper with an independently supplied alignment layer.

    Arguments:
        aligner: alignment layer used without model or network calls
    Returns:
        configured guided transcriber
    """
    return GuidedTranscriber(
        language=Language.eng,
        guide_language=Language.eng,
        spec=WhisperModelSpec(
            name="test/model", revision="test-revision", languages={Language.eng: "en"}
        ),
        aligner=aligner,
    )
