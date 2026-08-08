#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for mocked local pyannote speaker diarization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, call

from pydub import AudioSegment
from pytest import MonkeyPatch, raises

from scinoephile.audio.diarization import (
    PyannoteDiarizer,
    SpeakerDiarizationAuthorizationError,
)


@dataclass(frozen=True)
class _FakeSegment:
    """Minimal pyannote Segment stand-in."""

    start: float
    """Segment start time."""
    end: float
    """Segment end time."""


class _FakeAnnotation:
    """Minimal pyannote Annotation stand-in."""

    def __init__(self, turns: list[tuple[float, float, str]]):
        """Initialize.

        Arguments:
            turns: start, end, and speaker tuples
        """
        self.turns = turns

    def itertracks(self, *, yield_label: bool):
        """Iterate turns in pyannote's track shape.

        Arguments:
            yield_label: whether to include speaker labels
        """
        assert yield_label
        for start, end, speaker in self.turns:
            yield _FakeSegment(start, end), None, speaker


class _FakePipeline:
    """Minimal callable pyannote pipeline stand-in."""

    def __init__(self):
        """Initialize."""
        self.call_count = 0
        self.device = None
        self.kwargs: dict[str, object] = {}

    def __call__(self, audio: object, **kwargs: object) -> object:
        """Return regular and exclusive mocked annotations.

        Arguments:
            audio: in-memory waveform mapping
            **kwargs: speaker-count constraints
        Returns:
            pyannote output stand-in
        """
        assert isinstance(audio, dict)
        self.call_count += 1
        self.kwargs = kwargs
        return SimpleNamespace(
            speaker_diarization=_FakeAnnotation(
                [(0.0, 0.8, "SPEAKER_00"), (0.6, 1.0, "SPEAKER_01")]
            ),
            exclusive_speaker_diarization=_FakeAnnotation(
                [(0.0, 0.7, "SPEAKER_00"), (0.7, 1.0, "SPEAKER_01")]
            ),
        )

    def to(self, device: object):
        """Record selected device.

        Arguments:
            device: Torch device stand-in
        """
        self.device = device


class _FakeTorch:
    """Minimal Torch stand-in for in-memory waveform conversion."""

    @staticmethod
    def device(name: str) -> str:
        """Return a device identifier."""
        return name

    @staticmethod
    def from_numpy(value: object) -> object:
        """Return a waveform array unchanged."""
        return value


def test_diarizer_converts_turns_and_reuses_whole_audio_cache(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """A mocked whole-source pipeline should run once across repeat calls.

    Arguments:
        tmp_path: temporary cache root path
        monkeypatch: pytest monkeypatch fixture
    """
    pipeline = _FakePipeline()
    from_pretrained = Mock(return_value=pipeline)
    pipeline_cls = SimpleNamespace(from_pretrained=from_pretrained)
    embedding_path = "/cache/hbredin--wespeaker/speaker-embedding.onnx"
    hf_hub_download = Mock(side_effect=[tmp_path / "config.yaml", embedding_path])
    safe_load = Mock(
        return_value={
            "pipeline": {
                "name": "pyannote.audio.pipelines.SpeakerDiarization",
                "params": {},
            },
            "version": "3.0.0",
        }
    )
    (tmp_path / "config.yaml").write_text("pipeline: {}", encoding="utf-8")
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_huggingface_hub",
        lambda: SimpleNamespace(hf_hub_download=hf_hub_download),
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_pyannote_audio",
        lambda: SimpleNamespace(Pipeline=pipeline_cls),
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_torch", lambda: _FakeTorch
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_yaml",
        lambda: SimpleNamespace(safe_load=safe_load),
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.version", lambda name: "4.0.7"
    )
    audio = AudioSegment.silent(duration=1000, frame_rate=16000)
    diarizer = PyannoteDiarizer(
        tmp_path, device="cpu", num_speakers=2, overwrite_cache=False
    )

    first = diarizer(audio)
    second = diarizer(audio)

    assert first == second
    assert hf_hub_download.call_args_list == [
        call(
            "pyannote/speaker-diarization-3.0",
            "config.yaml",
            revision="61bc5e801239695154ba03562a72e1d6254ed4e4",
        ),
        call(
            "hbredin/wespeaker-voxceleb-resnet34-LM",
            "speaker-embedding.onnx",
            revision="0ae88dcaf48cacdf741275d6d1a8101f45eee220",
        ),
    ]
    from_pretrained.assert_called_once()
    pipeline_config = from_pretrained.call_args.args[0]
    assert pipeline_config["pipeline"]["params"] == {
        "embedding": embedding_path,
        "plda": {
            "checkpoint": "pyannote/speaker-diarization-community-1",
            "revision": "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee",
            "subfolder": "plda",
        },
        "segmentation": {
            "checkpoint": "pyannote/segmentation-3.0",
            "revision": "e66f3d3b9eb0873085418a7b813d3b369bf160bb",
        },
    }
    assert pipeline.call_count == 1
    assert pipeline.device == "cpu"
    assert pipeline.kwargs == {"num_speakers": 2}
    assert len(first.turns) == 2
    assert first.turns[0].end > first.turns[1].start
    assert [turn.speaker for turn in first.exclusive_turns] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]
    metadata = diarizer._get_cache_metadata()  # noqa: SLF001
    assert metadata["embedding_model_revision"] == (
        "0ae88dcaf48cacdf741275d6d1a8101f45eee220"
    )
    assert metadata["plda_model_revision"] == (
        "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee"
    )
    assert metadata["segmentation_model_revision"] == (
        "e66f3d3b9eb0873085418a7b813d3b369bf160bb"
    )


def test_cache_identity_separates_exact_model_revisions(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Different exact model revisions should never share diarization output.

    Arguments:
        tmp_path: temporary cache root path
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.version", lambda name: "4.0.7"
    )
    audio = AudioSegment.silent(duration=1000)
    first = PyannoteDiarizer(tmp_path, device="cpu", model_revision="revision-a")
    second = PyannoteDiarizer(tmp_path, device="cpu", model_revision="revision-b")

    first_path = first._cache.get_path(  # noqa: SLF001
        audio,
        first._get_cache_metadata(),  # noqa: SLF001
    )
    second_path = second._cache.get_path(  # noqa: SLF001
        audio,
        second._get_cache_metadata(),  # noqa: SLF001
    )

    assert first_path != second_path


def test_diarizer_reports_gated_model_authorization(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """A missing gated pipeline should raise a clear authorization error.

    Arguments:
        tmp_path: temporary cache root path
        monkeypatch: pytest monkeypatch fixture
    """
    pipeline_cls = SimpleNamespace(from_pretrained=lambda config: None)
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_pyannote_audio",
        lambda: SimpleNamespace(Pipeline=pipeline_cls),
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.version", lambda name: "4.0.7"
    )
    monkeypatch.setattr(
        PyannoteDiarizer, "_load_pinned_pipeline_config", lambda self: {}
    )
    diarizer = PyannoteDiarizer(tmp_path, device="cpu")

    with raises(SpeakerDiarizationAuthorizationError, match="conditions"):
        diarizer(AudioSegment.silent(duration=1000))
