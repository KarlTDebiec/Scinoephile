#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Audio cache namespace declarations."""

from __future__ import annotations

from scinoephile.core.cache.cache_namespace import CacheNamespace

__all__ = ["AudioCacheNamespace"]


class AudioCacheNamespace(CacheNamespace):
    """Cache namespaces owned by the audio package."""

    SEPARATION_DEMUCS = "audio/separation/demucs"
    """Demucs-separated audio."""
    TRANSCRIPTION_MLX_AUDIO = "audio/transcription/mlx_audio"
    """MLX-Audio transcription results."""
    TRANSCRIPTION_WHISPER = "audio/transcription/whisper"
    """Whisper transcription results."""
    VAD = "audio/vad"
    """Voice activity detection traces."""
