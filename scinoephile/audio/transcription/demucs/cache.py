#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Caches Demucs-separated vocals."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory

from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError, CouldntEncodeError

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_root_path

__all__ = ["DemucsCache"]

logger = getLogger(__name__)

_CACHE_VERSION = 1
"""Current Demucs cache version."""


class DemucsCache:
    """Caches separated vocals by audio and Demucs model configuration."""

    def __init__(
        self,
        cache_root_path: Path | None,
        model_name: str,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            model_name: Demucs model name used for source separation
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which separated vocals are cached."""
        self.cache_dir_path = val_output_dir_path(self.cache_root_path / "demucs")
        """Directory in which cached vocals are stored."""

        self.model_name = model_name
        """Demucs model name identifying cached vocals."""

    def get_path(self, audio: AudioSegment) -> Path:
        """Get the cache path for audio and Demucs configuration.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            cache path
        """
        cache_hash = hashlib.sha256(audio.raw_data)
        cache_hash.update(b"\0")
        cache_hash.update(
            json.dumps(
                {
                    "audio_channels": audio.channels,
                    "audio_frame_rate": audio.frame_rate,
                    "audio_sample_width": audio.sample_width,
                    "cache_version": _CACHE_VERSION,
                    "model_name": self.model_name,
                },
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        )
        return self.cache_dir_path / f"{cache_hash.hexdigest()}.wav"

    def load(self, audio: AudioSegment) -> AudioSegment | None:
        """Load cached Demucs-separated vocals.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            cached vocals, if present
        Raises:
            ScinoephileError: if the cached audio cannot be read
        """
        cache_path = self.get_path(audio)
        if not cache_path.exists():
            return None

        try:
            vocals = AudioSegment.from_file(cache_path)
            cache_path.touch()
        except (CouldntDecodeError, OSError) as exc:
            raise ScinoephileError(
                f"Unable to read Demucs vocals cache {cache_path}: {exc}"
            ) from exc
        logger.info(f"Loaded Demucs vocals from cache: {cache_path}")
        return vocals

    def remove(self, audio: AudioSegment) -> Path | None:
        """Remove cached Demucs-separated vocals.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            removed cache path, if present
        """
        cache_path = self.get_path(audio)
        if not cache_path.exists():
            return None

        cache_path.unlink()
        logger.info(f"Removed Demucs vocals cache: {cache_path}")
        return cache_path

    def save(
        self,
        audio: AudioSegment,
        vocals: AudioSegment,
    ) -> Path:
        """Save Demucs-separated vocals to the cache.

        Arguments:
            audio: audio used to derive the cache key
            vocals: separated vocals to cache
        Returns:
            saved cache path
        Raises:
            ScinoephileError: if the cached audio cannot be written
        """
        cache_path = self.get_path(audio)
        # Export beside the target so replacement is atomic on the same filesystem
        try:
            with TemporaryDirectory(
                dir=cache_path.parent,
                prefix=f".{cache_path.stem}-",
            ) as temp_dir:
                staging_path = Path(temp_dir) / cache_path.name
                vocals.export(staging_path, format="wav")
                staging_path.replace(cache_path)
        except (CouldntEncodeError, OSError) as exc:
            raise ScinoephileError(
                f"Unable to write Demucs vocals cache {cache_path}: {exc}"
            ) from exc
        logger.info(f"Saved Demucs vocals to cache: {cache_path}")
        return cache_path
