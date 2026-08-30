#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of VAD detector orchestration."""

from __future__ import annotations

from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import numpy as np
import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import DemucsMode, TranscriptionEmptyError, VadMode
from scinoephile.audio.transcription.preprocessing_settings import (
    TranscriptionPreprocessingSettings,
)
from scinoephile.audio.transcription.whisper import (
    WHISPER_LARGE_V3_CANTONESE_MODEL,
    WhisperModel,
    WhisperTranscriber,
)
from scinoephile.audio.vad import (
    VadImplementation,
    VoiceActivityDetector,
    VoiceActivityError,
    VoiceActivityTrace,
)
from scinoephile.core import DependencyError, Language

_CUSTOM_MODEL = replace(
    WHISPER_LARGE_V3_CANTONESE_MODEL, name="custom/model", revision="custom-revision"
)


def test_pyannote_inference_uses_pinned_model_and_shared_interval_settings(
    monkeypatch: pytest.MonkeyPatch,
):
    """Run mocked pyannote VAD with pinned assets and shared interval settings.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    segmentation = SimpleNamespace(
        data=np.asarray(
            [
                [0, 0],
                [1, 0],
                [0, 1],
                [1, 1],
                [0, 0],
                [0, 0],
                [0, 0],
                [0, 0],
                [1, 0],
                [0, 1],
                [1, 1],
                [0, 0],
            ],
            dtype=np.float32,
        ),
        sliding_window=SimpleNamespace(start=0.05, duration=0.1, step=0.1),
    )
    pipeline = Mock()
    pipeline._segmentation = Mock(return_value=segmentation)
    pipeline_class = Mock(return_value=pipeline)
    model = object()
    model_class = SimpleNamespace(from_pretrained=Mock(return_value=model))
    from_numpy = Mock(return_value="waveform")
    device = Mock(return_value="cpu")
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.import_pyannote_audio",
        Mock(return_value=SimpleNamespace(Model=model_class)),
    )
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.import_pyannote_audio_voice_activity_detection",
        Mock(return_value=pipeline_class),
    )
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.import_torch",
        Mock(return_value=SimpleNamespace(device=device, from_numpy=from_numpy)),
    )
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
    )
    detector = VoiceActivityDetector(
        VadImplementation.PYANNOTE,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.3,
        padding_seconds=0.1,
    )
    audio = AudioSegment.silent(duration=1000, frame_rate=16000)

    assert detector(audio) == [(50, 550), (750, 1000)]
    get_snapshot_dir_path.assert_called_once_with(
        "pyannote/segmentation-3.0", "e66f3d3b9eb0873085418a7b813d3b369bf160bb"
    )
    model_class.from_pretrained.assert_called_once_with(Path("/cached/model"))
    pipeline_class.assert_called_once_with(segmentation=model)
    pipeline.to.assert_called_once_with("cpu")
    pipeline._segmentation.assert_called_once_with(
        {"sample_rate": 16000, "waveform": "waveform"}
    )
    waveform = from_numpy.call_args.args[0]
    assert waveform.dtype == "float32"
    assert waveform.shape == (1, 16000)


def test_pyannote_missing_authorization_is_a_domain_error(
    monkeypatch: pytest.MonkeyPatch,
):
    """Explain the gated model conditions when pyannote cannot load VAD assets.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    model_class = SimpleNamespace(from_pretrained=Mock(return_value=None))
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.import_pyannote_audio",
        Mock(return_value=SimpleNamespace(Model=model_class)),
    )
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.import_torch",
        Mock(return_value=SimpleNamespace()),
    )
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.get_huggingface_snapshot_dir_path",
        Mock(return_value=Path("/cached/model")),
    )
    detector = VoiceActivityDetector(VadImplementation.PYANNOTE)

    with pytest.raises(VoiceActivityError, match="Hugging Face conditions"):
        detector(AudioSegment.silent(duration=100))


def test_pyannote_rejects_unsupported_sample_rate():
    """Reject sample rates unsupported by pyannote's segmentation model."""
    with pytest.raises(ValueError, match="pyannote VAD requires 16000 Hz"):
        VoiceActivityDetector(VadImplementation.PYANNOTE, sample_rate=8000)


def test_rejects_unknown_implementation():
    """Reject an unknown implementation rather than silently selecting TEN."""
    with pytest.raises(ValueError, match="Unsupported VAD implementation"):
        VoiceActivityDetector(cast(VadImplementation, "unknown"))


@pytest.mark.parametrize(
    ("scores", "expected_intervals"),
    [([0.5], [(0, 100)]), ([0.0, 0.5], [(100, 200)]), ([0.5, 0.5], [(0, 200)])],
    ids=["threshold", "terminal", "complete"],
)
def test_pyannote_intervals_use_frame_boundaries_and_inclusive_threshold(
    scores: list[float], expected_intervals: list[tuple[int, int]]
):
    """Retain threshold-equal and terminal pyannote speech frames.

    Arguments:
        scores: mocked pyannote frame scores
        expected_intervals: expected half-open source-timeline intervals
    """
    detector = VoiceActivityDetector(
        VadImplementation.PYANNOTE,
        threshold=0.5,
        min_speech_duration_seconds=0.0,
        min_silence_duration_seconds=0.0,
        padding_seconds=0.0,
    )
    trace = VoiceActivityTrace(
        np.asarray(scores, dtype=np.float32),
        start_ms=50,
        step_ms=100,
        duration_ms=len(scores) * 100,
    )

    assert detector.get_speech_intervals(trace) == expected_intervals


def test_ten_probabilities_are_converted_to_padded_intervals():
    """Convert TEN frame probabilities using duration and silence thresholds."""
    detector = VoiceActivityDetector(
        VadImplementation.TEN,
        threshold=0.5,
        frame_size=160,
        sample_rate=16000,
        min_speech_duration_seconds=0.02,
        min_silence_duration_seconds=0.02,
        padding_seconds=0.01,
    )

    trace = VoiceActivityTrace(
        np.asarray(
            [0.0, 0.8, 0.9, 0.0, 0.8, 0.9, 0.0, 0.0, 0.0, 0.8, 0.0], dtype=np.float32
        ),
        start_ms=5,
        step_ms=10,
        duration_ms=105,
    )

    assert detector.get_speech_intervals(trace) == [(0, 70)]


def test_ten_inference_pads_final_frame_and_returns_original_timeline(
    monkeypatch: pytest.MonkeyPatch,
):
    """Run mocked TEN inference without downloading models or native artifacts.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    runtime_detector = Mock()
    runtime_detector.process.side_effect = [(0.8, 1), (0.9, 1), (0.0, 0), (0.0, 0)]
    ten_vad_class = Mock(return_value=runtime_detector)
    monkeypatch.setattr(
        "scinoephile.audio.vad.ten.import_ten_vad",
        Mock(return_value=SimpleNamespace(TenVad=ten_vad_class)),
    )
    detector = VoiceActivityDetector(
        VadImplementation.TEN,
        frame_size=160,
        sample_rate=16000,
        min_speech_duration_seconds=0.01,
        min_silence_duration_seconds=0.02,
        padding_seconds=0.0,
    )
    audio = AudioSegment.silent(duration=35, frame_rate=16000)

    assert detector(audio) == [(0, 20)]
    ten_vad_class.assert_called_once_with(hop_size=160, threshold=0.5)
    assert runtime_detector.process.call_count == 4
    assert all(
        call.args[0].shape == (160,) for call in runtime_detector.process.call_args_list
    )


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"sample_rate": 8000}, "sample rate of 16000 Hz"),
        ({"frame_size": 320}, "frame size must be 160 or 256"),
    ],
)
def test_ten_configuration_rejects_unsupported_audio_geometry(
    kwargs: dict[str, int], message: str
):
    """Reject sample rates and frame sizes unsupported by official TEN VAD.

    Arguments:
        kwargs: invalid TEN configuration
        message: expected validation error text
    """
    with pytest.raises(ValueError, match=message):
        VoiceActivityDetector(VadImplementation.TEN, **kwargs)


def test_silero_inference_uses_shared_interval_settings(
    monkeypatch: pytest.MonkeyPatch,
):
    """Derive Silero intervals from its reusable frame-level score trace.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    probabilities = [0.0] * 7 + [0.8] * 15 + [0.0] * 10
    model = Mock()
    model.side_effect = [
        SimpleNamespace(item=Mock(return_value=probability))
        for probability in probabilities
    ]
    load_silero_vad = Mock(return_value=model)
    monkeypatch.setattr(
        "scinoephile.audio.vad.silero.import_torch",
        Mock(
            return_value=SimpleNamespace(
                from_numpy=Mock(side_effect=lambda x: x), no_grad=nullcontext
            )
        ),
    )
    monkeypatch.setattr(
        "scinoephile.audio.vad.silero.import_silero_vad_load_silero_vad",
        Mock(return_value=load_silero_vad),
    )
    detector = VoiceActivityDetector(
        VadImplementation.SILERO,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.08,
        padding_seconds=0.1,
    )
    samples = np.full(16000, round(0.05 * np.iinfo(np.int16).max), dtype=np.int16)
    audio = AudioSegment(
        data=samples.tobytes(), sample_width=2, frame_rate=16000, channels=1
    )

    assert detector(audio) == [(94, 834)]
    load_silero_vad.assert_called_once_with(onnx=True, opset_version=16)
    model.reset_states.assert_called_once_with()
    assert model.call_count == 32
    first_frame = model.call_args_list[0].args[0]
    assert np.max(first_frame) == pytest.approx(0.05, abs=1e-4)


def test_silero_rejects_unsupported_sample_rate():
    """Reject sample rates incompatible with Silero trace geometry."""
    with pytest.raises(ValueError, match="Silero VAD requires.*16000 Hz"):
        VoiceActivityDetector(VadImplementation.SILERO, sample_rate=8000)


def test_ten_missing_runtime_is_a_dependency_error(monkeypatch: pytest.MonkeyPatch):
    """Propagate the shared dependency error for a missing TEN runtime.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        "scinoephile.audio.vad.ten.import_ten_vad",
        Mock(side_effect=DependencyError("missing TEN VAD dependency")),
    )
    detector = VoiceActivityDetector(VadImplementation.TEN)

    with pytest.raises(DependencyError, match="missing TEN VAD dependency"):
        detector(AudioSegment.silent(duration=100))


def test_vad_cache_identity_separates_implementation_and_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Separate transcription caches by VAD model, runtime, and postprocessing.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    monkeypatch.setattr(
        "scinoephile.audio.vad.silero.get_distribution_identity",
        Mock(
            side_effect=lambda distribution_name: {
                "distribution": distribution_name,
                "version": {"onnxruntime": "1.28.0", "silero-vad": "6.2.1"}[
                    distribution_name
                ],
            }
        ),
    )
    monkeypatch.setattr(
        "scinoephile.audio.vad.ten.get_distribution_identity",
        Mock(return_value={"distribution": "ten-vad", "version": "1.0.6.8"}),
    )
    audio = AudioSegment.silent(duration=100)
    silero = WhisperTranscriber(
        WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu"),
        Language.yue_hant,
        cache_root_path=tmp_path,
        vad_mode=VadMode.ON,
        vad_detector=VoiceActivityDetector(VadImplementation.SILERO),
    )
    ten = WhisperTranscriber(
        WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu"),
        Language.yue_hant,
        cache_root_path=tmp_path,
        vad_mode=VadMode.ON,
        vad_detector=VoiceActivityDetector(VadImplementation.TEN, threshold=0.6),
    )
    settings = TranscriptionPreprocessingSettings(False, True)

    silero_cache_identity = silero._get_cache_identity(audio, settings)
    ten_cache_identity = ten._get_cache_identity(audio, settings)

    assert silero_cache_identity["vad"] != ten_cache_identity["vad"]
    assert ten_cache_identity["vad"] == {
        "frame_size": 256,
        "implementation": "ten",
        "model": "ten-vad-native",
        "min_silence_duration_seconds": 1.0,
        "min_speech_duration_seconds": 0.1,
        "padding_seconds": 0.5,
        "postprocessing_version": 2,
        "runtime": {"distribution": "ten-vad", "version": "1.0.6.8"},
        "sample_rate": 16000,
        "threshold": 0.6,
        "trace_identity_version": 2,
    }
    assert silero_cache_identity["vad"] == {
        "implementation": "silero",
        "model": "silero-vad",
        "model_format": "onnx",
        "model_opset": 16,
        "min_silence_duration_seconds": 1.0,
        "min_speech_duration_seconds": 0.1,
        "padding_seconds": 0.5,
        "postprocessing_version": 2,
        "runtime": {
            "onnxruntime": {"distribution": "onnxruntime", "version": "1.28.0"},
            "silero_vad": {"distribution": "silero-vad", "version": "6.2.1"},
        },
        "sample_rate": 16000,
        "threshold": 0.5,
        "trace_identity_version": 2,
    }
    assert silero._cache.get_path(audio, silero_cache_identity) != ten._cache.get_path(
        audio, ten_cache_identity
    )


def test_vad_trace_cache_identity_excludes_interval_postprocessing(
    monkeypatch: pytest.MonkeyPatch,
):
    """Reuse one TEN score trace across threshold and interval parameter sweeps.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        "scinoephile.audio.vad.ten.get_distribution_identity",
        Mock(return_value={"distribution": "ten-vad", "version": "1.0.6.8"}),
    )
    first = VoiceActivityDetector(
        VadImplementation.TEN,
        threshold=0.4,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.3,
        padding_seconds=0.1,
    )
    second = VoiceActivityDetector(
        VadImplementation.TEN,
        threshold=0.8,
        min_speech_duration_seconds=0.7,
        min_silence_duration_seconds=1.2,
        padding_seconds=0.5,
    )

    assert first.cache_identity != second.cache_identity
    assert first.trace_cache_identity == second.trace_cache_identity
    assert (
        first.cache_identity["trace_identity_version"]
        == first.trace_cache_identity["trace_identity_version"]
    )


def test_vad_cache_identity_pins_pyannote_model_and_runtime(
    monkeypatch: pytest.MonkeyPatch,
):
    """Identify pyannote VAD by its pinned model and installed runtime version.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        "scinoephile.audio.vad.pyannote.get_distribution_identity",
        Mock(return_value={"distribution": "pyannote.audio", "version": "4.0.7"}),
    )
    detector = VoiceActivityDetector(
        VadImplementation.PYANNOTE,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.3,
        padding_seconds=0.1,
    )

    assert detector.cache_identity == {
        "implementation": "pyannote",
        "min_silence_duration_seconds": 0.3,
        "min_speech_duration_seconds": 0.2,
        "model": "pyannote/segmentation-3.0",
        "model_revision": "e66f3d3b9eb0873085418a7b813d3b369bf160bb",
        "padding_seconds": 0.1,
        "postprocessing_version": 2,
        "runtime": {
            "pyannote_audio": {"distribution": "pyannote.audio", "version": "4.0.7"}
        },
        "sample_rate": 16000,
        "threshold": 0.5,
        "trace_identity_version": 2,
    }


def test_whisper_receives_explicit_ten_intervals(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Supply TEN intervals to Whisper Timestamped on the original timeline.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    trace = VoiceActivityTrace(
        np.ones(47, dtype=np.float32), start_ms=8, step_ms=16, duration_ms=1500
    )
    vad_detector = Mock(
        implementation=VadImplementation.TEN,
        cache_identity={"implementation": "ten", "model": "test"},
        trace_cache_identity={"implementation": "ten", "trace": "test"},
        threshold=0.5,
    )
    vad_detector.get_trace.return_value = trace
    vad_detector.get_speech_intervals.return_value = [(100, 400), (900, 1200)]
    transcribe = Mock(return_value={"segments": []})
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )
    transcriber = WhisperTranscriber(
        WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu"),
        Language.yue_hant,
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.ON,
        vad_detector=vad_detector,
    )
    transcriber.model.model = Mock()
    audio = AudioSegment.silent(duration=1500)

    assert transcriber(audio) == []
    vad_detector.get_trace.assert_called_once_with(audio)
    vad_detector.get_speech_intervals.assert_called_once_with(trace)
    assert transcribe.call_args.kwargs["vad"] == [(0.1, 0.4), (0.9, 1.2)]


def test_whisper_auto_retries_after_ten_unsupported_platform(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Retry without VAD when official TEN rejects the current platform.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    ten_vad_class = Mock(
        side_effect=NotImplementedError("Unsupported platform: Test unknown")
    )
    monkeypatch.setattr(
        "scinoephile.audio.vad.ten.import_ten_vad",
        Mock(return_value=SimpleNamespace(TenVad=ten_vad_class)),
    )
    vad_detector = VoiceActivityDetector(VadImplementation.TEN)
    transcribe = Mock(return_value={"segments": []})
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )
    transcriber = WhisperTranscriber(
        WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu"),
        Language.yue_hant,
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.AUTO,
        vad_detector=vad_detector,
    )
    transcriber.model.model = Mock()

    assert transcriber(AudioSegment.silent(duration=100)) == []
    ten_vad_class.assert_called_once_with(hop_size=256, threshold=0.5)
    assert transcribe.call_args.kwargs["vad"] is False


def test_whisper_ten_empty_output_skips_inference(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Treat TEN audio without detected speech as an empty VAD attempt.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary cache directory path
    """
    trace = VoiceActivityTrace(
        np.zeros(7, dtype=np.float32), start_ms=8, step_ms=16, duration_ms=100
    )
    vad_detector = Mock(
        implementation=VadImplementation.TEN,
        cache_identity={"implementation": "ten", "model": "test"},
        trace_cache_identity={"implementation": "ten", "trace": "test"},
        threshold=0.5,
    )
    vad_detector.get_trace.return_value = trace
    vad_detector.get_speech_intervals.return_value = []
    transcribe = Mock()
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper.model.import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )
    transcriber = WhisperTranscriber(
        WhisperModel(_CUSTOM_MODEL, Language.yue_hant, device="cpu"),
        Language.yue_hant,
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VadMode.ON,
        vad_detector=vad_detector,
    )

    with pytest.raises(TranscriptionEmptyError, match="TEN VAD found no speech"):
        transcriber(AudioSegment.silent(duration=100))

    transcribe.assert_not_called()
