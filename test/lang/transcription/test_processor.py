#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription processing."""

from __future__ import annotations

from logging import INFO
from unittest.mock import Mock, patch

from pydub import AudioSegment
from pydub.generators import Sine
from pytest import LogCaptureFixture, approx, raises

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.audio.transcription import TranscribedSegment, TranscribedWord
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.aligner import TranscriptionAligner
from scinoephile.lang.transcription.alignment import TranscriptionAlignment
from scinoephile.lang.transcription.processor import (
    DemucsMode,
    GuidedTranscriptionProcessor,
    VADMode,
)


def _get_processor(
    *,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VADMode = VADMode.OFF,
) -> tuple[GuidedTranscriptionProcessor, Mock]:
    """Get a processor with a passthrough alignment mock.

    Arguments:
        demucs_mode: Demucs preprocessing mode
        vad_mode: Whisper VAD mode
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
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
        ),
        aligner,
    )


def _get_segment(
    *,
    segment_id: int = 0,
    start: float = 0.1,
    end: float = 0.2,
    text: str = "hello",
    compression_ratio: float | None = None,
    with_words: bool = False,
) -> TranscribedSegment:
    """Get a minimal transcribed segment.

    Arguments:
        segment_id: segment identifier
        start: segment start in seconds
        end: segment end in seconds
        text: segment text
        compression_ratio: gzip compression ratio reported by Whisper
        with_words: whether to include word-level timings
    Returns:
        transcribed segment
    """
    words = None
    if with_words:
        words = [TranscribedWord(text=text, start=start, end=end, confidence=1.0)]
    return TranscribedSegment(
        id=segment_id,
        seek=0,
        start=start,
        end=end,
        text=text,
        compression_ratio=compression_ratio,
        words=words,
    )


def test_segments_are_usable_rejects_repetitive_whisper_output():
    """Test highly compressible Whisper loops are unusable for alignment."""
    segments = [
        _get_segment(
            compression_ratio=16.24,
            with_words=True,
        )
    ]

    assert not GuidedTranscriptionProcessor._segments_are_usable(segments)


def test_segments_are_usable_rejects_nonpositive_word_duration():
    """Test text-bearing words must remain positive after ms conversion."""
    segment = _get_segment(
        start=4.02,
        end=4.04,
        text=" 啊",
        compression_ratio=1.0,
    )
    segment.words = [
        TranscribedWord(text=" ", start=4.02, end=4.04, confidence=1.0),
        TranscribedWord(text="啊", start=4.04, end=4.04, confidence=1.0),
    ]

    assert not GuidedTranscriptionProcessor._segments_are_usable([segment])


def test_segments_are_usable_rejects_timestamp_beyond_audio():
    """Test Whisper timestamps extending beyond source audio are unusable."""
    segments = [
        _get_segment(
            end=12.0,
            compression_ratio=1.0,
            with_words=True,
        )
    ]

    assert not GuidedTranscriptionProcessor._segments_are_usable(
        segments,
        audio_duration=10.0,
    )


def test_segments_are_usable_accepts_partial_guided_tail():
    """Test guide coverage does not determine transcription validity."""
    segments = [
        _get_segment(
            end=4.0,
            compression_ratio=1.0,
            with_words=True,
        )
    ]

    assert GuidedTranscriptionProcessor._segments_are_usable(
        segments,
        audio_duration=10.0,
    )


def test_missing_guided_tail_runs_focused_recovery():
    """Test a missing guided tail triggers normalized focused recovery."""
    processor, _ = _get_processor(vad_mode=VADMode.OFF)
    initial_segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]
    recovered_segments = [
        _get_segment(
            start=0.2,
            end=0.8,
            text="tail",
            compression_ratio=1.0,
            with_words=True,
        )
    ]
    recovered_segments[0].no_speech_prob = 0.1
    processor.no_vad_transcriber = Mock()
    processor.no_vad_transcriber.get_cached_transcription.return_value = (
        initial_segments
    )
    processor.tail_recovery_transcriber = Mock(return_value=recovered_segments)
    processor.tail_recovery_transcriber.get_cached_transcription.return_value = None
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = processor._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output[:1] == initial_segments
    assert output[1].text == "tail"
    assert output[1].start == 5.2
    assert output[1].end == 5.8
    normalized_tail_audio = processor.tail_recovery_transcriber.call_args.args[0]
    processor.tail_recovery_transcriber.assert_called_once_with(
        normalized_tail_audio,
        use_cache=False,
    )
    assert len(normalized_tail_audio) == 5000
    assert normalized_tail_audio.max_dBFS == approx(-1.0, abs=0.01)


def test_missing_guided_tail_keeps_base_after_unusable_cached_recovery():
    """Test an unusable focused-tail cache prevents redundant recovery."""
    processor, _ = _get_processor(vad_mode=VADMode.OFF)
    initial_segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    processor.no_vad_transcriber = Mock()
    processor.no_vad_transcriber.get_cached_transcription.return_value = (
        initial_segments
    )
    processor.tail_recovery_transcriber = Mock()
    processor.tail_recovery_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = processor._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output == initial_segments
    normalized_tail_audio = (
        processor.tail_recovery_transcriber.get_cached_transcription.call_args.args[0]
    )
    assert len(normalized_tail_audio) == 5000
    assert normalized_tail_audio.max_dBFS == approx(-1.0, abs=0.01)
    processor.tail_recovery_transcriber.get_cached_transcription.assert_called_once_with(
        normalized_tail_audio
    )
    processor.tail_recovery_transcriber.assert_not_called()


def test_missing_guided_tail_keeps_valid_base_without_credible_recovery():
    """Test implausible tail recovery does not invalidate a valid base transcript."""
    processor, _ = _get_processor(vad_mode=VADMode.OFF)
    initial_segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]
    stretched_segment = _get_segment(
        end=5.0,
        text="x",
        compression_ratio=1.0,
        with_words=True,
    )
    stretched_segment.no_speech_prob = 0.1
    no_speech_segment = _get_segment(
        segment_id=1,
        start=5.1,
        end=5.2,
        text="tail",
        compression_ratio=1.0,
        with_words=True,
    )
    no_speech_segment.no_speech_prob = 0.9
    processor.no_vad_transcriber = Mock()
    processor.no_vad_transcriber.get_cached_transcription.return_value = (
        initial_segments
    )
    processor.tail_recovery_transcriber = Mock(
        return_value=[stretched_segment, no_speech_segment]
    )
    processor.tail_recovery_transcriber.get_cached_transcription.return_value = None
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = processor._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output == initial_segments


def test_auto_vad_uses_cached_non_vad_result_after_repetitive_vad_result():
    """Test automatic VAD skips a repetitive cached result."""
    processor, _ = _get_processor(vad_mode=VADMode.AUTO)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    processor.vad_transcriber = Mock()
    processor.vad_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    processor.no_vad_transcriber = Mock()
    processor.no_vad_transcriber.get_cached_transcription.return_value = usable_segments

    output = processor._transcribe_block_audio(AudioSegment.silent(duration=1000))

    assert output == usable_segments
    processor.vad_transcriber.assert_not_called()
    processor.no_vad_transcriber.assert_not_called()


def test_rejected_cached_result_is_bypassed_for_fresh_retry():
    """Test a rejected cache entry does not prevent a fresh Whisper attempt."""
    processor, _ = _get_processor(vad_mode=VADMode.OFF)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    processor.no_vad_transcriber = Mock(return_value=usable_segments)
    processor.no_vad_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    processor.recovery_transcriber = Mock()
    processor.recovery_transcriber.get_cached_transcription.return_value = None
    audio = AudioSegment.silent(duration=1000)

    output = processor._transcribe_block_audio(audio)

    assert output == usable_segments
    processor.no_vad_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )


def test_auto_vad_retries_without_vad_after_repetitive_new_result():
    """Test automatic VAD retries without VAD after a repetitive new result."""
    processor, _ = _get_processor(vad_mode=VADMode.AUTO)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    processor.vad_transcriber = Mock(return_value=repetitive_segments)
    processor.vad_transcriber.get_cached_transcription.return_value = None
    processor.no_vad_transcriber = Mock(return_value=usable_segments)
    processor.no_vad_transcriber.get_cached_transcription.return_value = None
    audio = AudioSegment.silent(duration=1000)

    output = processor._transcribe_block_audio(audio)

    assert output == usable_segments
    processor.vad_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )
    processor.no_vad_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )


def test_unusable_no_vad_result_uses_defensive_recovery():
    """Test unusable non-VAD output is validated before defensive recovery."""
    processor, _ = _get_processor(vad_mode=VADMode.OFF)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    processor.no_vad_transcriber = Mock(return_value=repetitive_segments)
    processor.no_vad_transcriber.get_cached_transcription.return_value = None
    processor.recovery_transcriber = Mock(return_value=usable_segments)
    processor.recovery_transcriber.get_cached_transcription.return_value = None
    audio = AudioSegment.silent(duration=1000)

    output = processor._transcribe_block_audio(audio)

    assert output == usable_segments
    processor.no_vad_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )
    processor.recovery_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )


def test_all_unusable_candidates_fail_before_alignment():
    """Test unusable recovery output raises a transcription-domain error."""
    processor, _ = _get_processor(vad_mode=VADMode.OFF)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    processor.no_vad_transcriber = Mock(return_value=repetitive_segments)
    processor.no_vad_transcriber.get_cached_transcription.return_value = None
    processor.recovery_transcriber = Mock(return_value=repetitive_segments)
    processor.recovery_transcriber.get_cached_transcription.return_value = None

    with raises(ScinoephileError, match="no usable transcription"):
        processor._transcribe_block_audio(AudioSegment.silent(duration=1000))


def test_auto_demucs_retries_unseparated_audio_after_unusable_result():
    """Test automatic Demucs retries the original audio before recovery decoding."""
    processor, _ = _get_processor(
        demucs_mode=DemucsMode.AUTO,
        vad_mode=VADMode.OFF,
    )
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    processor.no_vad_transcriber = Mock(return_value=repetitive_segments)
    processor.no_vad_transcriber.get_cached_transcription.return_value = None
    processor.unseparated_no_vad_transcriber = Mock(return_value=usable_segments)
    processor.unseparated_no_vad_transcriber.get_cached_transcription.return_value = (
        None
    )
    processor.recovery_transcriber = Mock()
    processor.recovery_transcriber.get_cached_transcription.return_value = None
    original_audio = AudioSegment.silent(duration=1000)
    separated_audio = AudioSegment.silent(duration=900)
    processor.demucs_separator = Mock(return_value=separated_audio)

    output = processor._transcribe_block_audio(original_audio)

    assert output == usable_segments
    processor.demucs_separator.assert_called_once_with(original_audio)
    processor.no_vad_transcriber.assert_called_once_with(
        separated_audio,
        cache_audio=original_audio,
        use_cache=False,
    )
    processor.unseparated_no_vad_transcriber.assert_called_once_with(
        original_audio,
        cache_audio=original_audio,
        use_cache=False,
    )
    processor.recovery_transcriber.assert_not_called()


def test_auto_demucs_uses_original_audio_after_separation_failure():
    """Test automatic Demucs recovers when vocal separation fails."""
    processor, _ = _get_processor(
        demucs_mode=DemucsMode.AUTO,
        vad_mode=VADMode.OFF,
    )
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    processor.no_vad_transcriber = Mock()
    processor.no_vad_transcriber.get_cached_transcription.return_value = None
    processor.unseparated_no_vad_transcriber = Mock(return_value=usable_segments)
    processor.unseparated_no_vad_transcriber.get_cached_transcription.return_value = (
        None
    )
    processor.recovery_transcriber = Mock()
    processor.recovery_transcriber.get_cached_transcription.return_value = None
    original_audio = AudioSegment.silent(duration=1000)
    processor.demucs_separator = Mock(
        side_effect=ScinoephileError("Demucs separation failed.")
    )

    output = processor._transcribe_block_audio(original_audio)

    assert output == usable_segments
    processor.demucs_separator.assert_called_once_with(original_audio)
    processor.no_vad_transcriber.assert_not_called()
    processor.unseparated_no_vad_transcriber.assert_called_once_with(
        original_audio,
        cache_audio=original_audio,
        use_cache=False,
    )
    processor.recovery_transcriber.assert_not_called()


def test_forced_demucs_surfaces_separation_failure():
    """Test forced Demucs does not hide vocal-separation failures."""
    processor, _ = _get_processor(
        demucs_mode=DemucsMode.ON,
        vad_mode=VADMode.OFF,
    )
    processor.no_vad_transcriber = Mock()
    processor.no_vad_transcriber.get_cached_transcription.return_value = None
    processor.recovery_transcriber = Mock()
    processor.recovery_transcriber.get_cached_transcription.return_value = None
    original_audio = AudioSegment.silent(duration=1000)
    processor.demucs_separator = Mock(
        side_effect=ScinoephileError("Demucs separation failed.")
    )

    with raises(ScinoephileError, match="Demucs separation failed"):
        processor._transcribe_block_audio(original_audio)

    processor.demucs_separator.assert_called_once_with(original_audio)
    processor.no_vad_transcriber.assert_not_called()
    processor.recovery_transcriber.assert_not_called()


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
    ) as transcribe_block_audio:
        output = processor.process_block(audio_block, reference_block)

    assert len(output) == 1
    assert output[0].text == "hello"
    assert output[0].start == 350
    assert output[0].end == 450
    transcribe_block_audio.assert_called_once_with(
        audio_block.audio,
        expected_last_start=0.75,
    )
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


def test_process_uses_exclusive_stop_index(caplog: LogCaptureFixture):
    """Test stop_at_idx excludes that block while logs use one-based numbers.

    Arguments:
        caplog: captured log records
    """
    processor, _ = _get_processor()
    caplog.set_level(INFO, logger="scinoephile.lang.transcription.processor")
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
    assert "BLOCK 1:" in caplog.text
    assert "BLOCK 0:" not in caplog.text


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
