#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media audio extraction cache."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.media import AudioStream
from scinoephile.core.paths import get_runtime_cache_dir_path

__all__ = ["get_media_audio_cache_path"]

_AUDIO_CACHE_VERSION = 1
"""Cache key version for normalized extracted audio."""


def get_media_audio_cache_path(
    infile_path: Path,
    stream: AudioStream,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Get the cache path for normalized extracted audio.

    Arguments:
        infile_path: media input file
        stream: audio stream to extract
        cache_dir_path: cache directory path
    Returns:
        extracted audio cache path
    """
    if cache_dir_path is None:
        cache_dir_path = get_runtime_cache_dir_path("media", "audio")
    else:
        cache_dir_path = val_output_dir_path(cache_dir_path)

    stat = infile_path.stat()
    payload = {
        "version": _AUDIO_CACHE_VERSION,
        "path": str(infile_path),
        "size": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "stream_index": stream.index,
        "codec_name": stream.codec_name,
        "channels": stream.channels,
        "output_format": "wav",
        "output_sample_rate": 16000,
        "output_channels": 1,
        "downmix": _get_downmix_name(stream),
    }
    encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
    cache_key = hashlib.sha256(encoded_payload).hexdigest()
    return cache_dir_path / cache_key / "audio.wav"


def _get_downmix_name(stream: AudioStream) -> str:
    """Get cache key name for the audio downmix operation.

    Arguments:
        stream: audio stream to extract
    Returns:
        downmix operation name
    """
    if stream.channels is not None and stream.channels >= 6:
        return "center-channel"
    return "mono-downmix"
