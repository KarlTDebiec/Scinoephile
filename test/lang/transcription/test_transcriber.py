#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription processing."""

from __future__ import annotations

from logging import INFO
from typing import cast
from unittest.mock import Mock, patch

from pydub import AudioSegment
from pydub.generators import Sine
from pytest import LogCaptureFixture, approx, raises

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.audio.transcription import (
    MimoTranscriber,
    MimoTranscriptionError,
    TranscribedSegment,
    TranscribedWord,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.aligner import TranscriptionAligner
from scinoephile.lang.transcription.alignment import TranscriptionAlignment
from scinoephile.lang.transcription.transcriber import (
    DemucsMode,
    GuidedTranscriber,
    TranscriptionBackend,
    VADMode,
)


def _get_transcriber(
    *,
    backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VADMode = VADMode.OFF,
) -> tuple[GuidedTranscriber, Mock]:
    """Get a transcriber with a passthrough alignment mock.

    Arguments:
        backend: audio transcription backend
        demucs_mode: Demucs preprocessing mode
        vad_mode: voice activity detection mode
    Returns:
        transcriber and alignment mock
    """
    aligner = Mock(spec=TranscriptionAligner)
    aligner.align.side_effect = TranscriptionAlignment
    aligner.delineation_processor = Mock()
    aligner.delineation_processor.prune_test_cases = False
    aligner.punctuation_processor = Mock()
    aligner.punctuation_processor.prune_test_cases = False
    mimo_transcriber = None
    unseparated_mimo_transcriber = None
    if backend == TranscriptionBackend.MIMO:
        mimo_transcriber = Mock(spec=MimoTranscriber)
        if demucs_mode == DemucsMode.AUTO:
            unseparated_mimo_transcriber = Mock(spec=MimoTranscriber)
    return (
        GuidedTranscriber(
            language=Language.eng,
            reference_language=Language.zho_hans,
            model_name="test/model",
            whisper_language="en",
            aligner=aligner,
            backend=backend,
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            mimo_transcriber=mimo_transcriber,
            unseparated_mimo_transcriber=unseparated_mimo_transcriber,
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

    assert not GuidedTranscriber._segments_are_usable(segments)


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

    assert not GuidedTranscriber._segments_are_usable([segment])


def test_segments_are_usable_rejects_timestamp_beyond_audio():
    """Test Whisper timestamps extending beyond source audio are unusable."""
    segments = [
        _get_segment(
            end=12.0,
            compression_ratio=1.0,
            with_words=True,
        )
    ]

    assert not GuidedTranscriber._segments_are_usable(
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

    assert GuidedTranscriber._segments_are_usable(
        segments,
        audio_duration=10.0,
    )


def test_missing_guided_tail_runs_focused_recovery():
    """Test a missing guided tail triggers normalized focused recovery."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.OFF)
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
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = (
        initial_segments
    )
    transcriber.tail_recovery_transcriber = Mock(return_value=recovered_segments)
    transcriber.tail_recovery_transcriber.get_cached_transcription.return_value = None
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = transcriber._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output[:1] == initial_segments
    assert output[1].text == "tail"
    assert output[1].start == 5.2
    assert output[1].end == 5.8
    normalized_tail_audio = transcriber.tail_recovery_transcriber.call_args.args[0]
    transcriber.tail_recovery_transcriber.assert_called_once_with(
        normalized_tail_audio,
        use_cache=False,
    )
    assert len(normalized_tail_audio) == 5000
    assert normalized_tail_audio.max_dBFS == approx(-1.0, abs=0.01)


def test_missing_guided_tail_keeps_base_after_unusable_cached_recovery():
    """Test an unusable focused-tail cache prevents redundant recovery."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.OFF)
    initial_segments = [_get_segment(end=4.0, compression_ratio=1.0, with_words=True)]
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = (
        initial_segments
    )
    transcriber.tail_recovery_transcriber = Mock()
    transcriber.tail_recovery_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = transcriber._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output == initial_segments
    normalized_tail_audio = (
        transcriber.tail_recovery_transcriber.get_cached_transcription.call_args.args[0]
    )
    assert len(normalized_tail_audio) == 5000
    assert normalized_tail_audio.max_dBFS == approx(-1.0, abs=0.01)
    transcriber.tail_recovery_transcriber.get_cached_transcription.assert_called_once_with(
        normalized_tail_audio
    )
    transcriber.tail_recovery_transcriber.assert_not_called()


def test_missing_guided_tail_keeps_valid_base_without_credible_recovery():
    """Test implausible tail recovery does not invalidate a valid base transcript."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.OFF)
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
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = (
        initial_segments
    )
    transcriber.tail_recovery_transcriber = Mock(
        return_value=[stretched_segment, no_speech_segment]
    )
    transcriber.tail_recovery_transcriber.get_cached_transcription.return_value = None
    audio = Sine(440).to_audio_segment(duration=10000).apply_gain(-20.0)

    output = transcriber._transcribe_block_audio(audio, expected_last_start=8.0)

    assert output == initial_segments


def test_auto_vad_uses_cached_non_vad_result_after_repetitive_vad_result():
    """Test automatic VAD skips a repetitive cached result."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.AUTO)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.vad_transcriber = Mock()
    transcriber.vad_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = (
        usable_segments
    )

    output = transcriber._transcribe_block_audio(AudioSegment.silent(duration=1000))

    assert output == usable_segments
    transcriber.vad_transcriber.assert_not_called()
    transcriber.no_vad_transcriber.assert_not_called()


def test_rejected_cached_result_skips_repeated_decode():
    """Test a rejected cache entry is not decoded again on a later run."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.OFF)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    transcriber.recovery_transcriber = Mock(return_value=usable_segments)
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None
    audio = AudioSegment.silent(duration=1000)

    output = transcriber._transcribe_block_audio(audio)

    assert output == usable_segments
    transcriber.no_vad_transcriber.assert_not_called()
    transcriber.recovery_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )


def test_rejected_cached_recovery_is_decoded():
    """Test a rejected cached recovery transcription is retried."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.OFF)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    transcriber.recovery_transcriber = Mock(return_value=usable_segments)
    transcriber.recovery_transcriber.get_cached_transcription.return_value = (
        repetitive_segments
    )
    audio = AudioSegment.silent(duration=1000)

    output = transcriber._transcribe_block_audio(audio)

    assert output == usable_segments
    transcriber.no_vad_transcriber.assert_not_called()
    transcriber.recovery_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )


def test_auto_vad_retries_without_vad_after_repetitive_new_result():
    """Test automatic VAD retries without VAD after a repetitive new result."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.AUTO)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.vad_transcriber = Mock(return_value=repetitive_segments)
    transcriber.vad_transcriber.get_cached_transcription.return_value = None
    transcriber.no_vad_transcriber = Mock(return_value=usable_segments)
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    audio = AudioSegment.silent(duration=1000)

    output = transcriber._transcribe_block_audio(audio)

    assert output == usable_segments
    transcriber.vad_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )
    transcriber.no_vad_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )


def test_unusable_no_vad_result_uses_defensive_recovery():
    """Test unusable non-VAD output is validated before defensive recovery."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.OFF)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.no_vad_transcriber = Mock(return_value=repetitive_segments)
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock(return_value=usable_segments)
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None
    audio = AudioSegment.silent(duration=1000)

    output = transcriber._transcribe_block_audio(audio)

    assert output == usable_segments
    transcriber.no_vad_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )
    transcriber.recovery_transcriber.assert_called_once_with(
        audio,
        cache_audio=audio,
        use_cache=False,
    )


def test_all_unusable_candidates_leave_gap_for_translation():
    """Test unusable recovery output leaves an empty transcription block."""
    transcriber, _ = _get_transcriber(vad_mode=VADMode.OFF)
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    transcriber.no_vad_transcriber = Mock(return_value=repetitive_segments)
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock(return_value=repetitive_segments)
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None

    output = transcriber._transcribe_block_audio(AudioSegment.silent(duration=1000))

    assert output == []


def test_mimo_backend_retries_original_audio_after_unusable_demucs_result():
    """Test automatic Demucs retries original audio using MiMo only."""
    transcriber, _ = _get_transcriber(
        backend=TranscriptionBackend.MIMO,
        demucs_mode=DemucsMode.AUTO,
        vad_mode=VADMode.AUTO,
    )
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(text="mimo", with_words=True)]
    assert transcriber.mimo_transcriber is not None
    assert transcriber.unseparated_mimo_transcriber is not None
    primary = cast(Mock, transcriber.mimo_transcriber)
    unseparated = cast(Mock, transcriber.unseparated_mimo_transcriber)
    primary.get_cached_transcription.return_value = None
    primary.return_value = repetitive_segments
    unseparated.get_cached_transcription.return_value = None
    unseparated.return_value = usable_segments
    original_audio = AudioSegment.silent(duration=1000)
    separated_audio = AudioSegment.silent(duration=900)
    transcriber.demucs_separator = Mock(return_value=separated_audio)

    output = transcriber._transcribe_block_audio(original_audio)

    assert output == usable_segments
    assert primary.call_count == 1
    assert primary.call_args.args == (separated_audio,)
    assert primary.call_args.kwargs == {
        "cache_audio": original_audio,
        "use_cache": False,
    }
    assert unseparated.call_count == 1
    assert unseparated.call_args.args == (original_audio,)
    assert unseparated.call_args.kwargs == {
        "cache_audio": original_audio,
        "use_cache": False,
    }
    assert transcriber.vad_transcriber is None
    assert transcriber.recovery_transcriber is None


def test_failed_mimo_backend_leaves_gap_for_translation():
    """Test a MiMo failure preserves downstream gap translation behavior."""
    transcriber, _ = _get_transcriber(
        backend=TranscriptionBackend.MIMO,
        vad_mode=VADMode.OFF,
    )
    assert transcriber.mimo_transcriber is not None
    mimo = cast(Mock, transcriber.mimo_transcriber)
    mimo.get_cached_transcription.return_value = None
    mimo.side_effect = MimoTranscriptionError("MiMo failed")

    output = transcriber._transcribe_block_audio(AudioSegment.silent(duration=1000))

    assert output == []
    assert transcriber.no_vad_transcriber is None
    assert transcriber.recovery_transcriber is None


def test_auto_demucs_retries_unseparated_audio_after_unusable_result():
    """Test automatic Demucs retries the original audio before recovery decoding."""
    transcriber, _ = _get_transcriber(
        demucs_mode=DemucsMode.AUTO,
        vad_mode=VADMode.OFF,
    )
    repetitive_segments = [_get_segment(compression_ratio=16.24, with_words=True)]
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.no_vad_transcriber = Mock(return_value=repetitive_segments)
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    transcriber.unseparated_no_vad_transcriber = Mock(return_value=usable_segments)
    transcriber.unseparated_no_vad_transcriber.get_cached_transcription.return_value = (
        None
    )
    transcriber.recovery_transcriber = Mock()
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None
    original_audio = AudioSegment.silent(duration=1000)
    separated_audio = AudioSegment.silent(duration=900)
    transcriber.demucs_separator = Mock(return_value=separated_audio)

    output = transcriber._transcribe_block_audio(original_audio)

    assert output == usable_segments
    transcriber.demucs_separator.assert_called_once_with(original_audio)
    transcriber.no_vad_transcriber.assert_called_once_with(
        separated_audio,
        cache_audio=original_audio,
        use_cache=False,
    )
    transcriber.unseparated_no_vad_transcriber.assert_called_once_with(
        original_audio,
        cache_audio=original_audio,
        use_cache=False,
    )
    transcriber.recovery_transcriber.assert_not_called()


def test_auto_demucs_uses_original_audio_after_separation_failure():
    """Test automatic Demucs recovers when vocal separation fails."""
    transcriber, _ = _get_transcriber(
        demucs_mode=DemucsMode.AUTO,
        vad_mode=VADMode.OFF,
    )
    usable_segments = [_get_segment(compression_ratio=1.0, with_words=True)]
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    transcriber.unseparated_no_vad_transcriber = Mock(return_value=usable_segments)
    transcriber.unseparated_no_vad_transcriber.get_cached_transcription.return_value = (
        None
    )
    transcriber.recovery_transcriber = Mock()
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None
    original_audio = AudioSegment.silent(duration=1000)
    transcriber.demucs_separator = Mock(
        side_effect=ScinoephileError("Demucs separation failed.")
    )

    output = transcriber._transcribe_block_audio(original_audio)

    assert output == usable_segments
    transcriber.demucs_separator.assert_called_once_with(original_audio)
    transcriber.no_vad_transcriber.assert_not_called()
    transcriber.unseparated_no_vad_transcriber.assert_called_once_with(
        original_audio,
        cache_audio=original_audio,
        use_cache=False,
    )
    transcriber.recovery_transcriber.assert_not_called()


def test_forced_demucs_surfaces_separation_failure():
    """Test forced Demucs does not hide vocal-separation failures."""
    transcriber, _ = _get_transcriber(
        demucs_mode=DemucsMode.ON,
        vad_mode=VADMode.OFF,
    )
    transcriber.no_vad_transcriber = Mock()
    transcriber.no_vad_transcriber.get_cached_transcription.return_value = None
    transcriber.recovery_transcriber = Mock()
    transcriber.recovery_transcriber.get_cached_transcription.return_value = None
    original_audio = AudioSegment.silent(duration=1000)
    transcriber.demucs_separator = Mock(
        side_effect=ScinoephileError("Demucs separation failed.")
    )

    with raises(ScinoephileError, match="Demucs separation failed"):
        transcriber._transcribe_block_audio(original_audio)

    transcriber.demucs_separator.assert_called_once_with(original_audio)
    transcriber.no_vad_transcriber.assert_not_called()
    transcriber.recovery_transcriber.assert_not_called()


def test_process_block_preserves_raw_segments_and_uses_buffered_offset():
    """Test generic processing preserves segments and anchors buffered audio."""
    transcriber, aligner = _get_transcriber()
    audio_block = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=1000, end=1500, text="reference")],
    )
    audio_block.buffered_start = 250
    reference_block = Series(events=[Subtitle(start=1000, end=1500, text="reference")])
    segment = _get_segment()

    with patch.object(
        transcriber,
        "_transcribe_block_audio",
        return_value=[segment],
    ) as transcribe_block_audio:
        output = transcriber.process_block(audio_block, reference_block)

    assert len(output) == 1
    assert output[0].text == "hello"
    assert output[0].start == 350
    assert output[0].end == 450
    transcribe_block_audio.assert_called_once_with(
        audio_block.audio,
        expected_last_start=0.75,
    )
    aligner.update_all_test_cases.assert_not_called()


def test_process_block_applies_configured_segment_splitter():
    """Test language specs may split raw Whisper segments."""
    transcriber, aligner = _get_transcriber()
    transcriber.segment_splitter = Mock(
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
        transcriber,
        "_transcribe_block_audio",
        return_value=[segment],
    ):
        transcriber.process_block(audio_block, reference_block)

    transcriber.segment_splitter.assert_called_once_with(segment)
    transcription = aligner.align.call_args.args[1]
    assert [subtitle.text for subtitle in transcription] == ["one", "two"]


def test_process_uses_exclusive_stop_index(caplog: LogCaptureFixture):
    """Test stop_at_idx excludes that block while logs use one-based numbers.

    Arguments:
        caplog: captured log records
    """
    transcriber, aligner = _get_transcriber()
    caplog.set_level(INFO, logger="scinoephile.lang.transcription.transcriber")
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
        transcriber,
        "process_block",
        side_effect=lambda audio_block, reference_block: audio_block,
    ) as process_block:
        output = transcriber.process(audio_series, reference_series, stop_at_idx=1)

    assert process_block.call_count == 1
    assert len(output) == 1
    assert output[0].text == "one"
    assert "BLOCK 1:" in caplog.text
    assert "BLOCK 0:" not in caplog.text
    aligner.update_all_test_cases.assert_called_once_with()


def test_process_uses_inclusive_start_index(caplog: LogCaptureFixture):
    """Test start_at_idx excludes earlier blocks while preserving global numbering.

    Arguments:
        caplog: captured log records
    """
    transcriber, _ = _get_transcriber()
    caplog.set_level(INFO, logger="scinoephile.lang.transcription.transcriber")
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
        transcriber,
        "process_block",
        side_effect=lambda audio_block, reference_block: audio_block,
    ) as process_block:
        output = transcriber.process(
            audio_series,
            reference_series,
            start_at_idx=1,
        )

    assert process_block.call_count == 1
    assert len(output) == 1
    assert output[0].text == "two"
    assert "BLOCK 2:" in caplog.text
    assert "BLOCK 1:" not in caplog.text


def test_process_rejects_mismatched_block_counts():
    """Test guided transcription requires corresponding block structures."""
    transcriber, _ = _get_transcriber()
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
        transcriber.process(audio_series, reference_series)


def test_process_rejects_partial_range_when_pruning_test_cases():
    """Test pruning requires processing every block."""
    transcriber, aligner = _get_transcriber()
    aligner.delineation_processor.prune_test_cases = True
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

    with raises(ValueError, match="Cannot prune test cases"):
        transcriber.process(audio_series, reference_series, stop_at_idx=1)

    aligner.update_all_test_cases.assert_not_called()


def test_process_does_not_save_test_cases_after_failure():
    """Test test cases are not persisted when processing fails."""
    transcriber, aligner = _get_transcriber()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="one")],
    )
    reference_series = Series(events=[Subtitle(start=0, end=1000, text="one")])

    with (
        patch.object(
            transcriber,
            "process_block",
            side_effect=ScinoephileError("transcription failed"),
        ),
        raises(ScinoephileError, match="transcription failed"),
    ):
        transcriber.process(audio_series, reference_series)

    aligner.update_all_test_cases.assert_not_called()


def test_process_rejects_negative_stop_index():
    """Test guided transcription rejects negative stop indexes."""
    transcriber, _ = _get_transcriber()
    audio_series = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[AudioSubtitle(start=0, end=1000, text="one")],
    )
    reference_series = Series(events=[Subtitle(start=0, end=1000, text="one")])

    with raises(ValueError, match="greater than or equal to 0"):
        transcriber.process(audio_series, reference_series, stop_at_idx=-1)
