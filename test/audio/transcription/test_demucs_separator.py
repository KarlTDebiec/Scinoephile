#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of DemucsSeparator."""

from __future__ import annotations

from unittest.mock import Mock, patch

import torch
from pydub import AudioSegment

from scinoephile.audio.transcription.demucs_separator import DemucsSeparator


def test_get_audio_segment_restores_mono_output():
    """Test separated stereo vocals can be restored to mono output."""
    vocals = torch.tensor([[0.25, -0.25], [0.25, -0.25]], dtype=torch.float32)

    audio = DemucsSeparator._get_audio_segment(
        vocals=vocals,
        frame_rate=16000,
        channels=1,
    )

    assert isinstance(audio, AudioSegment)
    assert audio.channels == 1


def test_separate_vocals_uses_default_demucs_shifts():
    """Test Demucs separation relies on library-default shift behavior."""
    separator = DemucsSeparator()
    separator._model = Mock(samplerate=16000, sources=["vocals"])
    separator._model.to.return_value = separator._model
    separator._model.eval.return_value = separator._model
    input_audio = AudioSegment.silent(duration=1000, frame_rate=16000).set_channels(1)
    separated_sources = torch.zeros((1, 1, 2, 16000), dtype=torch.float32)

    with patch(
        "scinoephile.audio.transcription.demucs_separator.apply_model",
        return_value=separated_sources,
    ) as patched_apply_model:
        output_audio = separator.separate_vocals(input_audio)

    assert isinstance(output_audio, AudioSegment)
    assert output_audio.frame_rate == input_audio.frame_rate
    patched_apply_model.assert_called_once()
    assert "shifts" not in patched_apply_model.call_args.kwargs
