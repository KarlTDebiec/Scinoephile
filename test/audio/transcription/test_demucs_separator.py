#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of DemucsSeparator."""

from __future__ import annotations

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
