#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of MlxAudioTranscriber."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import (
    CtcAligner,
    DemucsMode,
    TranscribedSegment,
    TranscribedWord,
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionInferenceError,
    TranscriptionPreprocessingSettings,
    VADMode,
)
from scinoephile.audio.transcription.mlx_audio.backend import (
    MIMO_MODEL_NAME,
    MlxAudioInferenceResult,
)
from scinoephile.audio.transcription.mlx_audio.transcriber import MlxAudioTranscriber
from scinoephile.core import Language


@pytest.fixture(autouse=True)
def use_apple_silicon_platform(monkeypatch: pytest.MonkeyPatch):
    """Run MLX-Audio transcriber tests as though on the supported platform."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.system",
        Mock(return_value="Darwin"),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.machine",
        Mock(return_value="arm64"),
    )


def _get_cache_path(
    transcriber: MlxAudioTranscriber,
    audio: AudioSegment,
    use_demucs: bool = False,
    use_vad: bool = False,
) -> Path:
    """Get the cache path for one preprocessing configuration."""
    settings = TranscriptionPreprocessingSettings(use_demucs, use_vad)
    cache_path = transcriber._cache.get_path(
        audio, transcriber._get_cache_metadata(settings)
    )
    assert cache_path is not None
    return cache_path


def test_init_defaults_preprocessing_to_auto():
    """Test MLX-Audio defaults both preprocessing dimensions to automatic."""
    transcriber = MlxAudioTranscriber()

    assert transcriber.demucs_mode is DemucsMode.AUTO
    assert transcriber.vad_mode is VADMode.AUTO


def test_get_cache_path_separates_model_configuration():
    """Test MLX-Audio cache paths differ by model configuration."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber(
        model_name="custom/MiMo-V2.5-ASR-one"
    )
    second_transcriber = _get_mlx_audio_transcriber(
        model_name="custom/MiMo-V2.5-ASR-two"
    )

    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path.parent == Path("/tmp/mlx-audio").resolve()
    assert second_cache_path.parent == Path("/tmp/mlx-audio").resolve()
    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_ctc_model_configuration():
    """Test MLX-Audio cache paths differ by CTC model configuration."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber()
    second_transcriber = _get_mlx_audio_transcriber()
    first_transcriber.ctc_aligner = CtcAligner(Language.yue_hant, "ctc/one")
    second_transcriber.ctc_aligner = CtcAligner(Language.yue_hant, "ctc/two")

    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path != second_cache_path


def test_get_cache_path_uses_mlx_runtime_on_apple_silicon():
    """Test cache metadata identifies the fixed MLX runtime."""
    transcriber = _get_mlx_audio_transcriber(model_name=MIMO_MODEL_NAME)

    metadata = transcriber._get_cache_metadata(
        TranscriptionPreprocessingSettings(False, False)
    )

    assert metadata["runtime"] == "mlx"


@pytest.mark.parametrize(
    ("system", "machine"),
    [("Linux", "arm64"), ("Darwin", "x86_64"), ("Windows", "ARM64")],
)
def test_init_rejects_unsupported_platform(
    monkeypatch: pytest.MonkeyPatch, system: str, machine: str
):
    """Test MLX-Audio fails during construction on unsupported platforms."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.system",
        Mock(return_value=system),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.mlx_audio.transcriber.platform.machine",
        Mock(return_value=machine),
    )

    with pytest.raises(TranscriptionError, match="requires macOS on Apple Silicon"):
        MlxAudioTranscriber()


def test_get_cache_path_separates_generation_options():
    """Test MLX-Audio cache paths differ by generation options."""
    audio = _get_cache_audio()
    first_transcriber = _get_mlx_audio_transcriber()
    second_transcriber = _get_mlx_audio_transcriber()
    second_transcriber.max_tokens = 1024

    first_cache_path = _get_cache_path(first_transcriber, audio)
    second_cache_path = _get_cache_path(second_transcriber, audio)

    assert first_cache_path != second_cache_path


def test_get_cache_path_separates_audio_formats():
    """Test MLX-Audio cache paths include audio format metadata."""
    raw_data = b"\0\1" * 100
    audio_segments = [
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=8000, channels=1),
        AudioSegment(data=raw_data, sample_width=2, frame_rate=16000, channels=2),
        AudioSegment(data=raw_data, sample_width=1, frame_rate=16000, channels=1),
    ]
    transcriber = _get_mlx_audio_transcriber()

    cache_paths = {
        _get_cache_path(transcriber, audio_segment) for audio_segment in audio_segments
    }

    assert len(cache_paths) == len(audio_segments)


def test_init_rejects_non_positive_max_tokens():
    """Test MLX-Audio rejects unusable generation token limits."""
    with pytest.raises(ValueError, match="MLX-Audio max tokens must be positive"):
        MlxAudioTranscriber(max_tokens=0)


def test_init_rejects_chunk_duration_that_rounds_to_zero():
    """Test chunk durations must advance by at least one millisecond."""
    with pytest.raises(ValueError, match="round to at least one millisecond"):
        MlxAudioTranscriber(chunk_duration_seconds=0.0004)


def test_get_cached_transcription_reads_mlx_audio_payload(tmp_path: Path):
    """Test MLX-Audio cache reads segment payloads from metadata-bearing files."""
    transcriber = MlxAudioTranscriber(
        cache_root_path=tmp_path, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF
    )
    audio = _get_cache_audio()
    expected_segments = [_get_timed_segment("你好")]
    transcriber._cache.save(
        audio,
        transcriber._get_cache_metadata(
            TranscriptionPreprocessingSettings(False, False)
        ),
        expected_segments,
    )

    segments = transcriber.get_cached_transcription(audio)

    assert segments == expected_segments


def test_transcribe_recovers_from_malformed_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test malformed cached output is replaced by a fresh transcription."""
    audio = _get_cache_audio()
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MlxAudioTranscriber(
        cache_root_path=tmp_path, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF
    )
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("{", encoding="utf-8")
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(transcriber, "_transcribe_attempt", patched_transcribe)

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_transcribe.assert_called_once_with(
        audio, TranscriptionPreprocessingSettings(False, False)
    )
    assert (
        json.loads(cache_path.read_text(encoding="utf-8"))["segments"][0]["text"]
        == "你好"
    )


def test_malformed_cache_does_not_override_fresh_rejection(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test a stale cache-read error does not replace fresh rejection behavior.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    audio = _get_cache_audio()
    fresh_segments = [_get_timed_segment("fresh")]
    transcriber = MlxAudioTranscriber(
        cache_root_path=tmp_path, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF
    )
    cache_path = _get_cache_path(transcriber, audio)
    cache_path.write_text("{", encoding="utf-8")
    monkeypatch.setattr(
        transcriber, "_transcribe_attempt", Mock(return_value=fresh_segments)
    )

    segments = transcriber.transcribe(audio, is_usable=lambda _segments: False)

    assert segments == []
    assert (
        json.loads(cache_path.read_text(encoding="utf-8"))["segments"][0]["text"]
        == "fresh"
    )


def test_transcribe_uses_direct_mlx_audio_inference(monkeypatch: pytest.MonkeyPatch):
    """Test MLX-Audio transcription uses direct typed inference."""
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MlxAudioTranscriber(
        model_name=MIMO_MODEL_NAME, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model", return_value=expected_segments
    )

    def fake_transcribe(
        audio_path: Path, max_tokens: int | None
    ) -> MlxAudioInferenceResult:
        """Capture direct MLX-Audio arguments and return transcript text."""
        captured.update(audio_path=audio_path, max_tokens=max_tokens)
        return MlxAudioInferenceResult(text="你好")

    monkeypatch.setattr(transcriber.backend, "transcribe", fake_transcribe)
    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    assert transcriber.model_name == MIMO_MODEL_NAME
    assert transcriber.backend.mlx_audio_language == "zh"
    assert captured["max_tokens"] == 256
    assert isinstance(captured["audio_path"], Path)


def test_transcribe_derives_language_and_passes_max_tokens(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test MLX-Audio derives language identifiers and forwards max tokens."""
    captured: dict[str, object] = {}
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MlxAudioTranscriber(
        model_name=MIMO_MODEL_NAME,
        language=Language.eng,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        max_tokens=1024,
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model", return_value=expected_segments
    )

    def fake_transcribe(
        _audio_path: Path, max_tokens: int | None
    ) -> MlxAudioInferenceResult:
        """Capture direct MLX-Audio arguments and return transcript text."""
        captured.update(max_tokens=max_tokens)
        return MlxAudioInferenceResult(text="你好")

    monkeypatch.setattr(transcriber.backend, "transcribe", fake_transcribe)
    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    assert transcriber.backend.mlx_audio_language == "en"
    assert captured["max_tokens"] == 1024


def test_transcribe_chunks_audio_and_offsets_segments(monkeypatch: pytest.MonkeyPatch):
    """Test MLX-Audio chunking offsets segments and drops overlap duplicates."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MlxAudioTranscriber(
        model_name=MIMO_MODEL_NAME,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        chunk_duration_seconds=2.0,
        chunk_overlap_seconds=0.5,
    )
    backend_transcribe = Mock(
        side_effect=[
            MlxAudioInferenceResult(text="one"),
            MlxAudioInferenceResult(text="two"),
            MlxAudioInferenceResult(text="three"),
        ]
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            [
                TranscribedSegment(
                    id=0,
                    seek=0,
                    start=0.1,
                    end=2.2,
                    text="duplicatetwo",
                    words=[
                        TranscribedWord(
                            text="duplicate", start=0.1, end=0.3, confidence=0.9
                        ),
                        TranscribedWord(text="two", start=0.7, end=2.2, confidence=0.9),
                    ],
                )
            ],
            [_get_timed_segment("three", start=0.6, end=1.0)],
        ],
    )
    monkeypatch.setattr(transcriber.backend, "transcribe", backend_transcribe)
    segments = transcriber.transcribe(audio)

    assert backend_transcribe.call_count == 3
    assert transcriber.ctc_aligner.call_count == 3
    assert [segment.text for segment in segments] == ["one", "two", "three"]
    assert [segment.id for segment in segments] == [0, 1, 2]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 2.2, 4.1])
    assert [segment.end for segment in segments] == pytest.approx([0.9, 3.7, 4.5])
    assert segments[1].words is not None
    assert segments[1].words[0].start == pytest.approx(2.2)
    assert segments[1].words[0].end == pytest.approx(3.7)


def test_transcribe_splits_audio_after_generation_token_exhaustion(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test truncated MLX-Audio output is retried over smaller windows."""
    audio = AudioSegment.silent(duration=4000)
    transcriber = MlxAudioTranscriber(
        demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF, chunk_overlap_seconds=0.0
    )
    backend_transcribe = Mock(
        side_effect=[
            MlxAudioInferenceResult(text="truncated", generation_tokens=256),
            MlxAudioInferenceResult(text="one", generation_tokens=1),
            MlxAudioInferenceResult(text="two", generation_tokens=1),
        ]
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model",
        side_effect=[
            [_get_timed_segment("one", end=2.0)],
            [_get_timed_segment("two", end=2.0)],
        ],
    )
    monkeypatch.setattr(transcriber.backend, "transcribe", backend_transcribe)
    segments = transcriber.transcribe(audio)

    assert backend_transcribe.call_count == 3
    assert transcriber.ctc_aligner.call_count == 2
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.start for segment in segments] == pytest.approx([0.0, 2.0])
    assert [segment.end for segment in segments] == pytest.approx([2.0, 4.0])


def test_transcribe_chunks_audio_skips_empty_windows(monkeypatch: pytest.MonkeyPatch):
    """Test an empty chunk does not discard speech from other chunks."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MlxAudioTranscriber(
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        chunk_duration_seconds=2.0,
        chunk_overlap_seconds=0.5,
    )
    patched_transcribe = Mock(
        side_effect=[
            [_get_timed_segment("one", start=0.1, end=0.9)],
            TranscriptionEmptyError("MLX-Audio returned empty transcript."),
            [_get_timed_segment("three", start=0.6, end=1.0)],
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_audio_window", patched_transcribe)

    segments = transcriber.transcribe(audio)

    assert patched_transcribe.call_count == 3
    assert [segment.text for segment in segments] == ["one", "three"]
    assert [segment.id for segment in segments] == [0, 1]
    assert [segment.start for segment in segments] == pytest.approx([0.1, 4.1])


def test_transcribe_chunks_audio_rejects_all_empty_windows(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test chunked transcription remains empty when every chunk is empty."""
    audio = AudioSegment.silent(duration=4500)
    transcriber = MlxAudioTranscriber(
        demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF, chunk_duration_seconds=2.0
    )
    monkeypatch.setattr(
        transcriber,
        "_transcribe_audio_window",
        Mock(
            side_effect=TranscriptionEmptyError("MLX-Audio returned empty transcript.")
        ),
    )

    with pytest.raises(TranscriptionEmptyError, match="across audio chunks"):
        transcriber.transcribe(audio)


def test_transcribe_vad_restores_original_timestamps(monkeypatch: pytest.MonkeyPatch):
    """Test MLX-Audio VAD removes silence and restores original word timings."""
    audio = AudioSegment.silent(duration=6000)
    transcriber = MlxAudioTranscriber(
        model_name=MIMO_MODEL_NAME, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.ON
    )
    monkeypatch.setattr(
        transcriber,
        "_get_vad_speech_intervals",
        Mock(return_value=[(1000, 2000), (4000, 5500)]),
    )
    patched_transcribe = Mock(
        return_value=[
            _get_timed_segment("one", start=0.1, end=0.9),
            _get_timed_segment("two", start=1.2, end=2.2),
        ]
    )
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)

    segments = transcriber.transcribe(audio)

    speech_audio = patched_transcribe.call_args.args[0]
    assert len(speech_audio) == 2500
    assert [segment.text for segment in segments] == ["one", "two"]
    assert [segment.id for segment in segments] == [0, 1]
    assert [segment.start for segment in segments] == pytest.approx([1.1, 4.2])
    assert [segment.end for segment in segments] == pytest.approx([1.9, 5.2])
    assert segments[1].words is not None
    assert segments[1].words[0].start == pytest.approx(4.2)
    assert segments[1].words[0].end == pytest.approx(5.2)


def test_transcribe_vad_rejects_audio_without_detected_speech(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test VAD does not invoke MLX-Audio when no speech is detected."""
    transcriber = MlxAudioTranscriber(
        model_name=MIMO_MODEL_NAME, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.ON
    )
    monkeypatch.setattr(transcriber, "_get_vad_speech_intervals", Mock(return_value=[]))
    patched_transcribe = Mock()
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)

    with pytest.raises(TranscriptionEmptyError, match="VAD found no speech"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    patched_transcribe.assert_not_called()


def test_transcribe_vad_auto_retries_unfiltered_audio(monkeypatch: pytest.MonkeyPatch):
    """Test automatic VAD retries unfiltered audio after VAD failure."""
    expected_segments = [_get_timed_segment("retry")]
    transcriber = MlxAudioTranscriber(
        model_name=MIMO_MODEL_NAME, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.AUTO
    )
    monkeypatch.setattr(transcriber, "_get_vad_speech_intervals", Mock(return_value=[]))
    patched_transcribe = Mock(return_value=expected_segments)
    monkeypatch.setattr(transcriber, "_transcribe_unfiltered_audio", patched_transcribe)
    audio = AudioSegment.silent(duration=1000)

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    patched_transcribe.assert_called_once_with(audio)


def test_transcribe_aligns_text_and_writes_cache(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Test transcription text is aligned, returned, and cached."""
    audio = AudioSegment.silent(duration=1000)
    expected_segments = [_get_timed_segment("你好")]
    transcriber = MlxAudioTranscriber(
        cache_root_path=tmp_path, demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF
    )
    monkeypatch.setattr(
        transcriber.backend,
        "transcribe",
        lambda _audio_path, _max_tokens: MlxAudioInferenceResult(text="你好"),
    )
    transcriber.ctc_aligner = Mock(
        model_name="ctc/test-model", return_value=expected_segments
    )

    segments = transcriber.transcribe(audio)

    assert segments == expected_segments
    transcriber.ctc_aligner.assert_called_once_with(audio, "你好")
    cache_path = _get_cache_path(transcriber, audio)
    cache_payload = json.loads(cache_path.read_text(encoding="utf-8"))
    assert cache_payload["cache_version"] == 1
    assert cache_payload["metadata"]["backend"] == "mlx-audio"
    assert cache_payload["metadata"]["model_family"] == "mimo"
    assert cache_payload["metadata"]["model_name"] == MIMO_MODEL_NAME
    assert cache_payload["segments"][0]["text"] == "你好"


def test_transcribe_rejects_low_information_vocalizations(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test isolated vocalizations do not become accepted transcription output.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    transcriber = MlxAudioTranscriber(demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF)
    monkeypatch.setattr(
        transcriber.backend,
        "transcribe",
        Mock(return_value=MlxAudioInferenceResult(text="啊！啊！")),
    )
    transcriber.ctc_aligner = Mock(model_name="ctc/test-model")

    with pytest.raises(TranscriptionError, match="low-information"):
        transcriber.transcribe(AudioSegment.silent(duration=1000))

    transcriber.ctc_aligner.assert_not_called()


def test_transcribe_wraps_mlx_audio_inference_errors(monkeypatch: pytest.MonkeyPatch):
    """Test MLX-Audio import/runtime errors are exposed as inference errors."""
    audio = AudioSegment.silent(duration=1000)
    transcriber = MlxAudioTranscriber(demucs_mode=DemucsMode.OFF, vad_mode=VADMode.OFF)
    monkeypatch.setattr(
        transcriber.backend,
        "transcribe",
        Mock(side_effect=ImportError("missing mlx_audio")),
    )

    with pytest.raises(
        TranscriptionInferenceError, match="Unable to run MLX-Audio inference"
    ):
        transcriber.transcribe(audio)


def _get_mlx_audio_transcriber(
    *, cache_root_path: Path = Path("/tmp"), model_name: str = MIMO_MODEL_NAME
) -> MlxAudioTranscriber:
    """Get an MLX-Audio transcriber with preprocessing disabled.

    Arguments:
        cache_root_path: root directory beneath which to cache
        model_name: MLX-Audio model name
    Returns:
        initialized transcriber
    """
    return MlxAudioTranscriber(
        model_name=model_name,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        cache_root_path=cache_root_path,
    )


def _get_cache_audio() -> AudioSegment:
    """Get a small audio segment suitable for MLX-Audio cache tests.

    Returns:
        audio segment with concrete format metadata
    """
    return AudioSegment(
        data=b"\0\1" * 100, sample_width=2, frame_rate=16000, channels=1
    )


def _get_timed_segment(
    text: str, *, start: float = 0.0, end: float = 1.0
) -> TranscribedSegment:
    """Get a segment with word timing data.

    Arguments:
        text: segment text
        start: start time in seconds
        end: end time in seconds
    Returns:
        segment with one timed word
    """
    return TranscribedSegment(
        id=0,
        seek=0,
        start=start,
        end=end,
        text=text,
        words=[TranscribedWord(text=text, start=start, end=end, confidence=0.9)],
    )
