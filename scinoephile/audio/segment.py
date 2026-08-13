#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydub audio segment loading and conversion."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

import numpy as np
from pydub import AudioSegment
from pydub.exceptions import PydubException

from scinoephile.common.file import get_temp_file_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.media.audio import AudioExtractionMode, extract_audio

__all__ = ["get_mono_pcm16_samples", "load_audio_segment"]

logger = getLogger(__name__)


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


def load_audio_segment(
    media_path: Path | str,
    *,
    stream_index: int | None = None,
    mode: AudioExtractionMode = AudioExtractionMode.ORIGINAL,
) -> AudioSegment:
    """Load a selected media audio stream as a pydub audio segment.

    Arguments:
        media_path: path to media file
        stream_index: absolute media stream index, or None for the first audio stream
        mode: channel preparation used during extraction
    Returns:
        complete extracted audio stream
    Raises:
        ScinoephileError: if the stream cannot be extracted or decoded
    """
    try:
        with get_temp_file_path(".wav") as temp_audio_path:
            extract_audio(
                media_path, temp_audio_path, stream_index=stream_index, mode=mode
            )
            logger.info(f"Loading audio from {temp_audio_path}")
            return AudioSegment.from_wav(temp_audio_path)
    except (OSError, PydubException, UnicodeError, ValueError) as exc:
        raise ScinoephileError(
            f"Unable to load audio from media {media_path}: {exc}"
        ) from exc
