#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of audio waveform conversion."""

from __future__ import annotations

import numpy as np
from pydub import AudioSegment
from pytest import approx

from scinoephile.audio.waveform import to_mono_int16


def test_to_mono_int16_converts_channel_rate_and_width():
    """Convert audio to a mono int16 waveform at the requested rate."""
    audio = (
        AudioSegment.silent(duration=100, frame_rate=8000)
        .set_channels(2)
        .set_sample_width(1)
    )

    waveform = to_mono_int16(audio, 12000)

    assert waveform.ndim == 1
    assert waveform.dtype == np.int16
    assert len(waveform) == approx(1200, abs=1)
    assert np.all(waveform == 0)
