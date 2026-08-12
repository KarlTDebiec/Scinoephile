#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of audio sample conversion."""

from __future__ import annotations

import numpy as np
import pytest
from pydub import AudioSegment

from scinoephile.audio.samples import get_mono_pcm16_samples


def test_get_mono_pcm16_samples_converts_channel_rate_and_width():
    """Convert audio to mono PCM16 samples at the requested rate."""
    audio = (
        AudioSegment.silent(duration=100, frame_rate=8000)
        .set_channels(2)
        .set_sample_width(1)
    )

    samples = get_mono_pcm16_samples(audio, 12000)

    assert samples.ndim == 1
    assert samples.dtype == np.int16
    assert len(samples) == pytest.approx(1200, abs=1)
    assert np.all(samples == 0)
