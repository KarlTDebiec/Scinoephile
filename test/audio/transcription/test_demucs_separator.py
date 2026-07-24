#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of DemucsSeparator."""

from __future__ import annotations

import builtins
from collections.abc import Mapping, Sequence
from unittest.mock import Mock, patch

import numpy as np
from pydub import AudioSegment
from pytest import MonkeyPatch, importorskip, raises

from scinoephile.audio.transcription.demucs_separator import DemucsSeparator


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

    audio = DemucsSeparator._get_audio_segment(
        vocals=vocals,
        frame_rate=16000,
        channels=1,
    )

    assert isinstance(audio, AudioSegment)
    assert audio.channels == 1


def test_demucs_model_loader_requires_transcription_extra(monkeypatch: MonkeyPatch):
    """Test Demucs import errors mention the transcription extra."""
    original_import = builtins.__import__

    def import_without_demucs(
        name: str,
        globals: Mapping[str, object] | None = None,
        locals: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        if name.split(".", 1)[0] == "demucs_infer":
            raise ImportError("blocked optional dependency")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", import_without_demucs)

    with raises(ImportError, match="'transcription' extra"):
        DemucsSeparator._import_demucs_infer_get_model()


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

    with patch.object(
        DemucsSeparator,
        "_import_demucs_infer_apply_model",
        return_value=apply_model,
    ):
        output_audio = separator.separate_vocals(input_audio)

    assert isinstance(output_audio, AudioSegment)
    assert output_audio.frame_rate == input_audio.frame_rate
    assert len(apply_model_kwargs) == 1
    assert "shifts" not in apply_model_kwargs[0]


def test_separate_vocals_overwrites_matching_cache(tmp_path, monkeypatch: MonkeyPatch):
    """Test cache overwrite regenerates a matching Demucs separation."""
    separator = DemucsSeparator(cache_dir_path=tmp_path)
    input_audio = AudioSegment.silent(duration=1000, frame_rate=16000)
    cached_audio = AudioSegment.silent(duration=900, frame_rate=16000)
    fresh_audio = AudioSegment.silent(duration=800, frame_rate=16000)
    separate = Mock(side_effect=[cached_audio, fresh_audio])
    monkeypatch.setattr(separator, "_separate_vocals_uncached", separate)

    separator.separate_vocals(input_audio)
    result = separator.separate_vocals(input_audio, overwrite_cache=True)

    assert len(result) == len(fresh_audio)
    assert separate.call_count == 2
    assert len(list(tmp_path.glob("*.wav"))) == 1
