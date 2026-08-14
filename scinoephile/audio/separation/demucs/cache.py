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

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.cache.artifact import remove_cache_artifact
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_root_path

__all__ = ["DemucsCache"]

logger = getLogger(__name__)

_CACHE_VERSION = 1
"""Current Demucs cache version."""


class DemucsCache:
    """Caches separated vocals by audio and Demucs model configuration."""

    def __init__(
        self, cache_root_path: Path | None, model_name: str, overwrite: bool = False
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            model_name: Demucs model name used for source separation
            overwrite: whether to replace matching cache files
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which separated vocals are cached."""
        self.cache_dir_path = AudioCacheNamespace.SEPARATION_DEMUCS.get_dir_path(
            self.cache_root_path
        )
        """Directory in which cached vocals are stored."""

        self.model_name = model_name
        """Demucs model name identifying cached vocals."""

        self.runtime_identity = get_distribution_identity("demucs-infer")
        """Installed Demucs runtime identity."""

        self.overwrite = overwrite
        """Whether matching cache files should be replaced."""

        self._refreshed_paths: set[Path] = set()
        """Cache paths refreshed by this cache instance."""

    @property
    def cache_identity(self) -> dict[str, object]:
        """Get the cache, model, and runtime identity for separated vocals."""
        return {
            "cache_version": _CACHE_VERSION,
            "model_name": self.model_name,
            "runtime": self.runtime_identity,
        }

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
                    "demucs": self.cache_identity,
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
        """
        cache_path = self.get_path(audio)
        if self.overwrite and cache_path not in self._refreshed_paths:
            self._refreshed_paths.add(cache_path)
            if remove_cache_artifact(cache_path):
                logger.info(f"Removed Demucs vocals cache: {cache_path}")
        if not cache_path.is_file() or cache_path.is_symlink():
            if remove_cache_artifact(cache_path):
                logger.warning(f"Discarded invalid Demucs vocals cache: {cache_path}")
            return None

        try:
            vocals = AudioSegment.from_file(cache_path)
            cache_path.touch()
        except (CouldntDecodeError, OSError) as exc:
            remove_cache_artifact(cache_path)
            logger.warning(f"Discarded invalid Demucs vocals cache {cache_path}: {exc}")
            return None
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
        if not remove_cache_artifact(cache_path):
            return None
        logger.info(f"Removed Demucs vocals cache: {cache_path}")
        return cache_path

    def save(self, audio: AudioSegment, vocals: AudioSegment) -> Path:
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
                dir=cache_path.parent, prefix=f".{cache_path.stem}-"
            ) as temp_dir:
                staging_path = Path(temp_dir) / cache_path.name
                vocals.export(staging_path, format="wav")
                staging_path.replace(cache_path)
        except (CouldntEncodeError, OSError) as exc:
            raise ScinoephileError(
                f"Unable to write Demucs vocals cache {cache_path}: {exc}"
            ) from exc
        self._refreshed_paths.add(cache_path)
        logger.info(f"Saved Demucs vocals to cache: {cache_path}")
        return cache_path
