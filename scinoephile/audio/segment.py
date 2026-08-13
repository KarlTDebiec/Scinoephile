#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydub audio segment loading."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from pydub import AudioSegment
from pydub.exceptions import PydubException

from scinoephile.common.file import get_temp_file_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.media.audio import AudioExtractionMode, extract_audio

__all__ = ["load_audio_segment"]

logger = getLogger(__name__)


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
