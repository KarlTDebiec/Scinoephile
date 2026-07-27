#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of DemucsSeparator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
from pydub import AudioSegment
from pytest import MonkeyPatch, importorskip

from scinoephile.audio.transcription.demucs import DemucsSeparator
from scinoephile.core.exceptions import ScinoephileError


class _NumpyBackedTensor:
    """Minimal tensor-shaped object for audio conversion tests."""

    def __init__(self, array: np.ndarray):
        """Initialize.

        Arguments:
            array: array returned by the numpy method
        """
        self._array = array

    def numpy(self) -> np.ndarray:
        """Return the wrapped numpy array."""
        return self._array


def test_get_audio_segment_restores_mono_output():
    """Test separated stereo vocals can be restored to mono output."""
    vocals = _NumpyBackedTensor(
        np.array([[0.25, -0.25], [0.25, -0.25]], dtype=np.float32)
    )

    audio = DemucsSeparator._get_audio_segment(vocals, 16000, 1)

    assert isinstance(audio, AudioSegment)
    assert audio.channels == 1


def test_separate_vocals_uses_default_demucs_shifts():
    """Test Demucs separation relies on library-default shift behavior."""
    torch = importorskip("torch")
    separator = DemucsSeparator()
    separator._model = Mock(samplerate=16000, sources=["vocals"])
    separator._model.to.return_value = separator._model
    separator._model.eval.return_value = separator._model
    input_audio = AudioSegment.silent(duration=1000, frame_rate=16000).set_channels(1)
    separated_sources = torch.zeros((1, 1, 2, 16000), dtype=torch.float32)
    apply_model_kwargs: list[dict[str, object]] = []

    def apply_model(*args: object, **kwargs: object) -> object:
        """Record Demucs apply_model keyword arguments."""
        assert args
        apply_model_kwargs.append(kwargs)
        return separated_sources

    with patch(
        "scinoephile.audio.transcription.demucs.separator.import_demucs_infer_apply",
        return_value=Mock(apply_model=apply_model),
    ):
        output_audio = separator.separate_vocals(input_audio)

    assert isinstance(output_audio, AudioSegment)
    assert output_audio.frame_rate == input_audio.frame_rate
    assert len(apply_model_kwargs) == 1
    assert "shifts" not in apply_model_kwargs[0]


def test_separate_vocals_overwrites_matching_cache(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test cache overwrite regenerates a matching Demucs separation."""
    separator = DemucsSeparator(cache_root_path=tmp_path)
    input_audio = AudioSegment.silent(duration=1000, frame_rate=16000)
    cached_audio = AudioSegment.silent(duration=900, frame_rate=16000)
    fresh_audio = AudioSegment.silent(duration=800, frame_rate=16000)
    separate = Mock(side_effect=[cached_audio, fresh_audio])
    monkeypatch.setattr(separator, "_separate_vocals", separate)

    separator.separate_vocals(input_audio)
    result = separator.separate_vocals(input_audio, overwrite_cache=True)

    assert len(result) == len(fresh_audio)
    assert separate.call_count == 2
    assert len(list((tmp_path / "demucs").glob("*.wav"))) == 1


def test_separate_vocals_recovers_from_corrupt_cache(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test malformed cached vocals are replaced by fresh separation output."""
    separator = DemucsSeparator(cache_root_path=tmp_path)
    input_audio = AudioSegment.silent(duration=1000, frame_rate=16000)
    fresh_audio = AudioSegment.silent(duration=800, frame_rate=16000)
    load = Mock(side_effect=ScinoephileError("invalid cache"))
    save = Mock()
    separate = Mock(return_value=fresh_audio)
    monkeypatch.setattr(separator._cache, "load", load)
    monkeypatch.setattr(separator._cache, "save", save)
    monkeypatch.setattr(separator, "_separate_vocals", separate)

    result = separator.separate_vocals(input_audio)

    assert result is fresh_audio
    load.assert_called_once_with(input_audio)
    separate.assert_called_once_with(input_audio)
    save.assert_called_once_with(input_audio, fresh_audio)
