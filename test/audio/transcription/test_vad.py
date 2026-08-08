#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared voice activity detection."""

from __future__ import annotations

from contextlib import nullcontext
from json import dumps
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest
from pydub import AudioSegment

from scinoephile.audio.transcription import (
    DemucsMode,
    TranscriptionEmptyError,
    TranscriptionError,
    VADImplementation,
    VADMode,
    VoiceActivityDetector,
    VoiceActivityTrace,
)
from scinoephile.audio.transcription.preprocessing_settings import (
    TranscriptionPreprocessingSettings,
)
from scinoephile.audio.transcription.whisper_transcriber import WhisperTranscriber


def test_pyannote_inference_uses_pinned_model_and_shared_interval_settings(
    monkeypatch: pytest.MonkeyPatch,
):
    """Run mocked pyannote VAD with pinned assets and shared interval settings."""
    segmentation = SimpleNamespace(
        data=np.asarray(
            [[0], [1], [1], [1], [0], [0], [0], [0], [1], [1], [1], [0]],
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
        "scinoephile.audio.transcription.vad.import_pyannote_audio",
        Mock(return_value=SimpleNamespace(Model=model_class)),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad."
        "import_pyannote_audio_voice_activity_detection",
        Mock(return_value=pipeline_class),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_torch",
        Mock(return_value=SimpleNamespace(device=device, from_numpy=from_numpy)),
    )
    detector = VoiceActivityDetector(
        VADImplementation.PYANNOTE,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.3,
        padding_seconds=0.1,
    )
    audio = AudioSegment.silent(duration=1000, frame_rate=16000)

    assert detector(audio) == [(100, 600), (800, 1000)]
    model_class.from_pretrained.assert_called_once_with(
        "pyannote/segmentation-3.0", revision="e66f3d3b9eb0873085418a7b813d3b369bf160bb"
    )
    pipeline_class.assert_called_once_with(segmentation=model)
    pipeline.instantiate.assert_called_once_with(
        {"min_duration_off": 0.3, "min_duration_on": 0.2}
    )
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
    """Explain the gated model conditions when pyannote cannot load VAD assets."""
    model_class = SimpleNamespace(from_pretrained=Mock(return_value=None))
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_pyannote_audio",
        Mock(return_value=SimpleNamespace(Model=model_class)),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_torch",
        Mock(return_value=SimpleNamespace()),
    )
    detector = VoiceActivityDetector(VADImplementation.PYANNOTE)

    with pytest.raises(TranscriptionError, match="Hugging Face conditions"):
        detector(AudioSegment.silent(duration=100))


def test_pyannote_rejects_unsupported_sample_rate():
    """Reject sample rates unsupported by pyannote's segmentation model."""
    with pytest.raises(ValueError, match="pyannote VAD requires 16000 Hz"):
        VoiceActivityDetector(VADImplementation.PYANNOTE, sample_rate=8000)


def test_ten_probabilities_are_converted_to_padded_intervals():
    """Convert TEN frame probabilities using duration and silence thresholds."""
    detector = VoiceActivityDetector(
        VADImplementation.TEN,
        threshold=0.5,
        frame_size=160,
        sample_rate=16000,
        min_speech_duration_seconds=0.02,
        min_silence_duration_seconds=0.02,
        padding_seconds=0.01,
    )

    intervals = detector._get_speech_intervals_from_probabilities(
        [0.0, 0.8, 0.9, 0.0, 0.8, 0.9, 0.0, 0.0, 0.0, 0.8, 0.0], duration_ms=105
    )

    assert intervals == [(0, 70)]


def test_ten_inference_pads_final_frame_and_returns_original_timeline(
    monkeypatch: pytest.MonkeyPatch,
):
    """Run mocked TEN inference without downloading models or native artifacts."""
    runtime_detector = Mock()
    runtime_detector.process.side_effect = [(0.8, 1), (0.9, 1), (0.0, 0), (0.0, 0)]
    ten_vad_class = Mock(return_value=runtime_detector)
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_ten_vad",
        Mock(return_value=SimpleNamespace(TenVad=ten_vad_class)),
    )
    detector = VoiceActivityDetector(
        VADImplementation.TEN,
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
        VoiceActivityDetector(VADImplementation.TEN, **kwargs)


def test_silero_inference_uses_shared_interval_settings(
    monkeypatch: pytest.MonkeyPatch,
):
    """Derive Silero intervals from its reusable frame-level score trace."""
    probabilities = [0.0] * 7 + [0.8] * 15 + [0.0] * 10
    model = Mock()
    model.side_effect = [
        SimpleNamespace(item=Mock(return_value=probability))
        for probability in probabilities
    ]
    get_vad_segments = Mock(return_value=[])
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_torch",
        Mock(
            return_value=SimpleNamespace(
                from_numpy=Mock(side_effect=lambda x: x), no_grad=nullcontext
            )
        ),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_whisper_timestamped_transcribe",
        Mock(
            return_value=SimpleNamespace(
                _silero_vad_model={"v6.2": model}, get_vad_segments=get_vad_segments
            )
        ),
    )
    detector = VoiceActivityDetector(
        VADImplementation.SILERO,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.08,
        padding_seconds=0.1,
    )

    assert detector(AudioSegment.silent(duration=1000)) == [(94, 834)]
    model.reset_states.assert_called_once_with()
    assert model.call_count == 32
    assert get_vad_segments.call_args.kwargs == {
        "sample_rate": 16000,
        "output_sample": False,
        "min_speech_duration": 0.1,
        "min_silence_duration": 0.1,
        "dilatation": 0,
        "method": "silero:v6.2",
    }


def test_ten_missing_runtime_is_a_domain_error(monkeypatch: pytest.MonkeyPatch):
    """Explain TEN's separate installation and license when its runtime is absent."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_ten_vad",
        Mock(side_effect=ImportError("missing")),
    )
    detector = VoiceActivityDetector(VADImplementation.TEN)

    with pytest.raises(TranscriptionError, match="additional license conditions"):
        detector(AudioSegment.silent(duration=100))


def test_vad_cache_identity_separates_implementation_and_settings(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Separate transcription caches by VAD model, runtime, and postprocessing."""
    whisper_distribution = Mock(version="1.15.9")
    whisper_distribution.read_text.return_value = None
    ten_distribution = Mock(version="1.0.6.8")
    ten_distribution.read_text.return_value = dumps(
        {
            "url": "https://github.com/TEN-framework/ten-vad.git",
            "vcs_info": {
                "commit_id": "22a3bcd4509d0faaa8eef4881e8af5f39c178950",
                "requested_revision": "22a3bcd4509d0faaa8eef4881e8af5f39c178950",
                "vcs": "git",
            },
        }
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.distribution",
        Mock(
            side_effect=lambda name: {
                "ten-vad": ten_distribution,
                "whisper-timestamped": whisper_distribution,
            }[name]
        ),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad._get_distribution_artifact_sha256",
        Mock(side_effect=["whisper-adapter-digest", "ten-runtime-digest"]),
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad._get_silero_model_artifact_sha256",
        Mock(return_value="silero-model-digest"),
    )
    audio = AudioSegment.silent(duration=100)
    silero = WhisperTranscriber(
        model_name="custom/model",
        cache_root_path=tmp_path,
        vad_mode=VADMode.ON,
        vad_detector=VoiceActivityDetector(VADImplementation.SILERO),
    )
    ten = WhisperTranscriber(
        model_name="custom/model",
        cache_root_path=tmp_path,
        vad_mode=VADMode.ON,
        vad_detector=VoiceActivityDetector(VADImplementation.TEN, threshold=0.6),
    )
    settings = TranscriptionPreprocessingSettings(False, True)

    silero_metadata = silero._get_cache_metadata(audio, settings)
    ten_metadata = ten._get_cache_metadata(audio, settings)

    assert silero_metadata["vad"] != ten_metadata["vad"]
    assert ten_metadata["vad"] == {
        "cache_identity_version": "3",
        "frame_size": 256,
        "implementation": "ten",
        "model": "ten-vad-native",
        "model_version": "1.0.6.8",
        "min_silence_duration_seconds": 1.0,
        "min_speech_duration_seconds": 0.1,
        "padding_seconds": 0.5,
        "postprocessing_version": "2",
        "runtime": {
            "artifact_sha256": "ten-runtime-digest",
            "distribution": "ten-vad",
            "source_commit": "22a3bcd4509d0faaa8eef4881e8af5f39c178950",
            "source_requested_revision": ("22a3bcd4509d0faaa8eef4881e8af5f39c178950"),
            "source_url": "https://github.com/TEN-framework/ten-vad.git",
            "source_vcs": "git",
            "version": "1.0.6.8",
        },
        "sample_rate": 16000,
        "tested_revision": "22a3bcd4509d0faaa8eef4881e8af5f39c178950",
        "threshold": 0.6,
    }
    assert silero_metadata["vad"] == {
        "cache_identity_version": "3",
        "implementation": "silero",
        "model": "snakers4/silero-vad",
        "model_artifact_sha256": "silero-model-digest",
        "model_revision": "v6.2",
        "model_revision_commit": "be95df9152c0d7618fa1edfeb296fc3dae32376f",
        "model_version": "v6.2",
        "min_silence_duration_seconds": 1.0,
        "min_speech_duration_seconds": 0.1,
        "padding_seconds": 0.5,
        "postprocessing_version": "2",
        "runtime": {
            "artifact_sha256": "whisper-adapter-digest",
            "distribution": "whisper-timestamped",
            "version": "1.15.9",
        },
        "sample_rate": 16000,
        "threshold": 0.5,
    }
    assert silero._cache.get_path(audio, silero_metadata) != ten._cache.get_path(
        audio, ten_metadata
    )


def test_vad_cache_identity_memoizes_only_resolved_artifacts(
    monkeypatch: pytest.MonkeyPatch,
):
    """Recheck unavailable artifacts, then memoize and defensively copy identity."""
    distribution_identity = Mock(
        side_effect=[
            {"distribution": "whisper-timestamped", "version": "unavailable"},
            {
                "artifact_sha256": "adapter-digest",
                "distribution": "whisper-timestamped",
                "version": "1.15.9",
            },
        ]
    )
    model_artifact_sha256 = Mock(side_effect=[None, "model-digest"])
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad._get_distribution_identity",
        distribution_identity,
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad._get_silero_model_artifact_sha256",
        model_artifact_sha256,
    )
    detector = VoiceActivityDetector(VADImplementation.SILERO)

    unresolved_identity = detector.cache_identity
    resolved_identity = detector.cache_identity
    resolved_identity["model"] = "mutated"

    assert "unavailable_artifact_nonce" in unresolved_identity
    assert "unavailable_artifact_nonce" not in resolved_identity
    assert detector.cache_identity["model"] == "snakers4/silero-vad"
    assert distribution_identity.call_count == 2
    assert model_artifact_sha256.call_count == 2


def test_vad_trace_cache_identity_excludes_interval_postprocessing(
    monkeypatch: pytest.MonkeyPatch,
):
    """Reuse one TEN score trace across threshold and interval parameter sweeps."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad._get_distribution_identity",
        Mock(
            return_value={
                "artifact_sha256": "ten-runtime-digest",
                "distribution": "ten-vad",
                "version": "1.0.6.8",
            }
        ),
    )
    first = VoiceActivityDetector(
        VADImplementation.TEN,
        threshold=0.4,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.3,
        padding_seconds=0.1,
    )
    second = VoiceActivityDetector(
        VADImplementation.TEN,
        threshold=0.8,
        min_speech_duration_seconds=0.7,
        min_silence_duration_seconds=1.2,
        padding_seconds=0.5,
    )

    assert first.cache_identity != second.cache_identity
    assert first.trace_cache_identity == second.trace_cache_identity


def test_vad_cache_identity_pins_pyannote_model_and_runtime(
    monkeypatch: pytest.MonkeyPatch,
):
    """Identify pyannote VAD by its exact model and installed runtime artifacts."""
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad._get_distribution_identity",
        Mock(
            return_value={
                "artifact_sha256": "pyannote-runtime-digest",
                "distribution": "pyannote.audio",
                "version": "4.0.7",
            }
        ),
    )
    detector = VoiceActivityDetector(
        VADImplementation.PYANNOTE,
        min_speech_duration_seconds=0.2,
        min_silence_duration_seconds=0.3,
        padding_seconds=0.1,
    )

    assert detector.cache_identity == {
        "cache_identity_version": "3",
        "implementation": "pyannote",
        "min_silence_duration_seconds": 0.3,
        "min_speech_duration_seconds": 0.2,
        "model": "pyannote/segmentation-3.0",
        "model_revision": "e66f3d3b9eb0873085418a7b813d3b369bf160bb",
        "model_version": "e66f3d3b9eb0873085418a7b813d3b369bf160bb",
        "padding_seconds": 0.1,
        "postprocessing_version": "2",
        "runtime": {
            "artifact_sha256": "pyannote-runtime-digest",
            "distribution": "pyannote.audio",
            "version": "4.0.7",
        },
        "sample_rate": 16000,
        "threshold": 0.5,
    }


def test_whisper_receives_explicit_ten_intervals(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Supply TEN intervals to Whisper Timestamped on the original timeline."""
    trace = VoiceActivityTrace(
        np.ones(47, dtype=np.float32), start_ms=8, step_ms=16, duration_ms=1500
    )
    vad_detector = Mock(
        implementation=VADImplementation.TEN,
        cache_identity={"implementation": "ten", "model_version": "test"},
        trace_cache_identity={"implementation": "ten", "trace": "test"},
        threshold=0.5,
    )
    vad_detector.get_trace.return_value = trace
    vad_detector.get_speech_intervals.return_value = [(100, 400), (900, 1200)]
    transcribe = Mock(return_value={"segments": []})
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper_transcriber."
        "import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )
    transcriber = WhisperTranscriber(
        model_name="custom/model",
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.ON,
        vad_detector=vad_detector,
    )
    transcriber._model = Mock()
    audio = AudioSegment.silent(duration=1500)

    assert transcriber(audio) == []
    vad_detector.get_trace.assert_called_once_with(audio)
    vad_detector.get_speech_intervals.assert_called_once_with(trace)
    assert transcribe.call_args.kwargs["vad"] == [(0.1, 0.4), (0.9, 1.2)]


def test_whisper_auto_retries_after_ten_unsupported_platform(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Retry without VAD when official TEN rejects the current platform."""
    ten_vad_class = Mock(
        side_effect=NotImplementedError("Unsupported platform: Test unknown")
    )
    monkeypatch.setattr(
        "scinoephile.audio.transcription.vad.import_ten_vad",
        Mock(return_value=SimpleNamespace(TenVad=ten_vad_class)),
    )
    vad_detector = VoiceActivityDetector(VADImplementation.TEN)
    transcribe = Mock(return_value={"segments": []})
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper_transcriber."
        "import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )
    transcriber = WhisperTranscriber(
        model_name="custom/model",
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.AUTO,
        vad_detector=vad_detector,
    )
    transcriber._model = Mock()

    assert transcriber(AudioSegment.silent(duration=100)) == []
    ten_vad_class.assert_called_once_with(hop_size=256, threshold=0.5)
    assert transcribe.call_args.kwargs["vad"] is False


def test_whisper_ten_empty_output_skips_inference(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    """Treat TEN audio without detected speech as an empty VAD attempt."""
    trace = VoiceActivityTrace(
        np.zeros(7, dtype=np.float32), start_ms=8, step_ms=16, duration_ms=100
    )
    vad_detector = Mock(
        implementation=VADImplementation.TEN,
        cache_identity={"implementation": "ten", "model_version": "test"},
        trace_cache_identity={"implementation": "ten", "trace": "test"},
        threshold=0.5,
    )
    vad_detector.get_trace.return_value = trace
    vad_detector.get_speech_intervals.return_value = []
    transcribe = Mock()
    monkeypatch.setattr(
        "scinoephile.audio.transcription.whisper_transcriber."
        "import_whisper_timestamped",
        Mock(return_value=SimpleNamespace(transcribe=transcribe)),
    )
    transcriber = WhisperTranscriber(
        model_name="custom/model",
        cache_root_path=tmp_path,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.ON,
        vad_detector=vad_detector,
    )

    with pytest.raises(TranscriptionEmptyError, match="TEN VAD found no speech"):
        transcriber(AudioSegment.silent(duration=100))

    transcribe.assert_not_called()
