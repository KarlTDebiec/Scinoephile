#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription processing."""

from __future__ import annotations

from unittest.mock import Mock, patch

from pydub import AudioSegment
from pytest import raises

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.audio.transcription import TranscribedSegment
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.aligner import TranscriptionAligner
from scinoephile.lang.transcription.alignment import TranscriptionAlignment
from scinoephile.lang.transcription.processor import (
    GuidedTranscriptionProcessor,
    VADMode,
)


def _get_processor() -> tuple[GuidedTranscriptionProcessor, Mock]:
    """Get a processor with a passthrough alignment mock.

    Returns:
        processor and alignment mock
    """
    aligner = Mock(spec=TranscriptionAligner)
    aligner.align.side_effect = TranscriptionAlignment
    return (
        GuidedTranscriptionProcessor(
            language=Language.eng,
            reference_language=Language.zho_hans,
            model_name="test/model",
            whisper_language="en",
            aligner=aligner,
            vad_mode=VADMode.OFF,
        ),
        aligner,
    )


def _get_segment(
    *,
    segment_id: int = 0,
    start: float = 0.1,
    end: float = 0.2,
    text: str = "hello",
) -> TranscribedSegment:
    """Get a minimal transcribed segment.

    Arguments:
        segment_id: segment identifier
        start: segment start in seconds
        end: segment end in seconds
        text: segment text
    Returns:
        transcribed segment
    """
    return TranscribedSegment(
        id=segment_id,
        seek=0,
        start=start,
        end=end,
        text=text,
    )


def test_process_block_preserves_raw_segments_and_uses_buffered_offset():
    """Test generic processing preserves segments and anchors buffered audio."""
    processor, aligner = _get_processor()
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=1000, end=1500, text="reference")],
    )
    audio_block.buffered_start = 250
    reference_block = Series(events=[Subtitle(start=1000, end=1500, text="reference")])
    segment = _get_segment()

    with patch.object(
        processor,
        "_transcribe_block_audio",
        return_value=[segment],
    ):
        output = processor.process_block(audio_block, reference_block)

    assert len(output) == 1
    assert output[0].text == "hello"
    assert output[0].start == 350
    assert output[0].end == 450
    aligner.update_all_test_cases.assert_called_once_with()


def test_process_block_applies_configured_segment_splitter():
    """Test language specs may split raw Whisper segments."""
    processor, aligner = _get_processor()
    processor.segment_splitter = Mock(
        return_value=[
            _get_segment(segment_id=0, end=0.15, text="one"),
            _get_segment(segment_id=1, start=0.15, text="two"),
        ]
    )
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="reference")],
    )
    audio_block.buffered_start = 0
    reference_block = Series(events=[Subtitle(start=0, end=1000, text="reference")])
    segment = _get_segment()

    with patch.object(
        processor,
        "_transcribe_block_audio",
        return_value=[segment],
    ):
        processor.process_block(audio_block, reference_block)

    processor.segment_splitter.assert_called_once_with(segment)
    transcription = aligner.align.call_args.args[1]
    assert [subtitle.text for subtitle in transcription] == ["one", "two"]


def test_process_uses_exclusive_stop_index():
    """Test stop_at_idx excludes the block at that index."""
    processor, _ = _get_processor()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=6000),
        events=[
            AudioSubtitle(start=0, end=1000, text="one"),
            AudioSubtitle(start=5000, end=6000, text="two"),
        ],
    )
    reference_series = Series(
        events=[
            Subtitle(start=0, end=1000, text="one"),
            Subtitle(start=5000, end=6000, text="two"),
        ]
    )

    with patch.object(
        processor,
        "process_block",
        side_effect=lambda audio_block, reference_block: audio_block,
    ) as process_block:
        output = processor.process(audio_series, reference_series, stop_at_idx=1)

    assert process_block.call_count == 1
    assert len(output) == 1
    assert output[0].text == "one"


def test_process_rejects_mismatched_block_counts():
    """Test guided transcription requires corresponding block structures."""
    processor, _ = _get_processor()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=6000),
        events=[AudioSubtitle(start=0, end=1000, text="one")],
    )
    reference_series = Series(
        events=[
            Subtitle(start=0, end=1000, text="one"),
            Subtitle(start=5000, end=6000, text="two"),
        ]
    )

    with raises(ScinoephileError, match="Audio has 1 blocks"):
        processor.process(audio_series, reference_series)


def test_process_rejects_negative_stop_index():
    """Test guided transcription rejects negative stop indexes."""
    processor, _ = _get_processor()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="one")],
    )
    reference_series = Series(events=[Subtitle(start=0, end=1000, text="one")])

    with raises(ValueError, match="greater than or equal to 0"):
        processor.process(audio_series, reference_series, stop_at_idx=-1)
