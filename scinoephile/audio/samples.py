#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio sample conversion."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

__all__ = ["get_mono_pcm16_samples"]

if TYPE_CHECKING:
    from pydub import AudioSegment


def get_mono_pcm16_samples(audio: AudioSegment, sample_rate: int) -> np.ndarray:
    """Convert audio to mono PCM16 samples at the requested sample rate.

    Arguments:
        audio: source audio
        sample_rate: target sample rate
    Returns:
        mono PCM16 samples at the requested sample rate
    """
    converted_audio = (
        audio.set_channels(1).set_frame_rate(sample_rate).set_sample_width(2)
    )
    return np.array(converted_audio.get_array_of_samples(), dtype=np.int16)
