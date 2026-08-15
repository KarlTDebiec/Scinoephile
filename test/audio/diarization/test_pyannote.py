#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for mocked local pyannote speaker diarization."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

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

    def itertracks(
        self, *, yield_label: bool
    ) -> Iterator[tuple[_FakeSegment, None, str]]:
        """Iterate turns in pyannote's track shape.

        Arguments:
            yield_label: whether to include speaker labels
        Yields:
            segment, track, and speaker tuples
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
        """Return a device identifier.

        Arguments:
            name: requested device name
        Returns:
            requested device name
        """
        return name

    @staticmethod
    def from_numpy(value: object) -> object:
        """Return a waveform array unchanged.

        Arguments:
            value: NumPy waveform array
        Returns:
            supplied waveform array
        """
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
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_pyannote_audio",
        lambda: SimpleNamespace(Pipeline=pipeline_cls),
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_torch", lambda: _FakeTorch
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.version", lambda name: "4.0.7"
    )
    get_snapshot_dir_path = Mock(return_value=Path("/cached/model"))
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.get_huggingface_snapshot_dir_path",
        get_snapshot_dir_path,
    )
    audio = AudioSegment.silent(duration=1000, frame_rate=16000)
    diarizer = PyannoteDiarizer(
        tmp_path, device="cpu", num_speakers=2, overwrite_cache=False
    )

    first = diarizer(audio)
    second = diarizer(audio)

    assert first == second
    get_snapshot_dir_path.assert_called_once_with(
        "pyannote/speaker-diarization-community-1",
        "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee",
    )
    from_pretrained.assert_called_once_with(Path("/cached/model"))
    assert pipeline.call_count == 1
    assert pipeline.device == "cpu"
    assert pipeline.kwargs == {"num_speakers": 2}
    assert len(first.turns) == 2
    assert first.turns[0].end > first.turns[1].start
    assert [turn.speaker for turn in first.exclusive_turns] == [
        "SPEAKER_00",
        "SPEAKER_01",
    ]
    assert diarizer.cache_identity["model_revision"] == (
        "3533c8cf8e369892e6b79ff1bf80f7b0286a54ee"
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
        audio, first.cache_identity
    )
    second_path = second._cache.get_path(  # noqa: SLF001
        audio, second.cache_identity
    )

    assert first_path != second_path


def test_custom_model_uses_repository_default_revision(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """A custom model without a revision should use its repository default.

    Arguments:
        tmp_path: temporary cache root path
        monkeypatch: pytest monkeypatch fixture
    """
    pipeline = _FakePipeline()
    from_pretrained = Mock(return_value=pipeline)
    pipeline_cls = SimpleNamespace(from_pretrained=from_pretrained)
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_pyannote_audio",
        lambda: SimpleNamespace(Pipeline=pipeline_cls),
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_torch", lambda: _FakeTorch
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.get_huggingface_snapshot_dir_path",
        Mock(return_value=Path("/cached/custom-model")),
    )
    diarizer = PyannoteDiarizer(tmp_path, model_id="custom/model")

    diarizer._get_pipeline()  # noqa: SLF001

    from_pretrained.assert_called_once_with(Path("/cached/custom-model"))
    assert diarizer.model_revision is None


def test_diarizer_rejects_exact_and_bounded_speaker_counts(tmp_path: Path):
    """An exact speaker count should not be combined with count bounds.

    Arguments:
        tmp_path: temporary cache root path
    """
    with raises(ValueError, match="cannot be combined"):
        PyannoteDiarizer(tmp_path, num_speakers=2, min_speakers=1)


def test_diarizer_reports_gated_model_authorization(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """A missing gated pipeline should raise a clear authorization error.

    Arguments:
        tmp_path: temporary cache root path
        monkeypatch: pytest monkeypatch fixture
    """
    pipeline_cls = SimpleNamespace(from_pretrained=Mock(return_value=None))
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.import_pyannote_audio",
        lambda: SimpleNamespace(Pipeline=pipeline_cls),
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.version", lambda name: "4.0.7"
    )
    monkeypatch.setattr(
        "scinoephile.audio.diarization.pyannote.get_huggingface_snapshot_dir_path",
        Mock(return_value=Path("/cached/model")),
    )
    diarizer = PyannoteDiarizer(tmp_path, device="cpu")

    with raises(SpeakerDiarizationAuthorizationError, match="conditions"):
        diarizer(AudioSegment.silent(duration=1000))
