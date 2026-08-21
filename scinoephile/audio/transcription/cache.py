#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Caches timestamped audio transcription output."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.common.file import open_atomic_text_file
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.cache.artifact import remove_cache_artifact
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.paths import get_runtime_cache_root_path

from .exceptions import TranscriptionError, TranscriptionInferenceError
from .transcribed_segment import TranscribedSegment

__all__ = ["TranscriptionCache"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_CACHE_VERSION = 2
"""Current transcription cache version."""


class TranscriptionCache:
    """Caches timestamped transcription output by audio and backend configuration."""

    def __init__(
        self,
        cache_root_path: Path | None,
        cache_namespace: AudioCacheNamespace,
        backend_name: str,
        backend_label: str,
        overwrite: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            cache_namespace: registered transcription backend namespace
            backend_name: stable backend name stored in cache identity
            backend_label: human-readable backend name used in log messages
            overwrite: whether to replace matching cache files
        """
        self.backend_name = backend_name
        """Stable backend name stored in cache identity."""
        self.backend_label = backend_label
        """Human-readable backend name used in log messages."""
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which transcriptions are cached."""
        self.cache_dir_path = cache_namespace.get_dir_path(self.cache_root_path)
        """Directory in which cached transcriptions are stored."""

        self.overwrite = overwrite
        """Whether matching cache files should be replaced."""

        self._refreshed_paths: set[Path] = set()
        """Cache paths refreshed by this cache instance."""

    def get_path(self, audio: AudioSegment, cache_identity: CacheIdentity) -> Path:
        """Get the cache path for audio and backend configuration.

        Arguments:
            audio: audio used to derive the cache key
            cache_identity: backend configuration identifying the output
        Returns:
            cache path
        """
        cache_hash = hashlib.sha256(audio.raw_data)
        cache_hash.update(b"\0")
        cache_hash.update(
            json.dumps(
                self._get_cache_identity(audio, cache_identity),
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        )
        return self.cache_dir_path / f"{cache_hash.hexdigest()}.json"

    def load(
        self, audio: AudioSegment, cache_identity: CacheIdentity
    ) -> tuple[Path, list[TranscribedSegment]] | None:
        """Load a cached transcription.

        Arguments:
            audio: audio used to derive the cache key
            cache_identity: backend configuration identifying the output
        Returns:
            cache path and cached segments, if present
        """
        cache_path = self.get_path(audio, cache_identity)
        if self.overwrite and cache_path not in self._refreshed_paths:
            self._refreshed_paths.add(cache_path)
            if remove_cache_artifact(cache_path):
                logger.info(
                    f"Removed {self.backend_label} transcription cache: {cache_path}"
                )
        if not cache_path.is_file() or cache_path.is_symlink():
            if remove_cache_artifact(cache_path):
                logger.warning(
                    f"Discarded invalid {self.backend_label} transcription cache: "
                    f"{cache_path}"
                )
            return None

        # Validate the matching entry, discarding invalid data as a cache miss
        expected_cache_identity = self._get_cache_identity(audio, cache_identity)
        try:
            with cache_path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            if not isinstance(payload, Mapping):
                raise TranscriptionInferenceError(
                    f"Malformed {self.backend_label} transcription cache payload: "
                    f"{cache_path}"
                )
            if payload.get("cache_version") != _CACHE_VERSION:
                raise TranscriptionInferenceError(
                    f"Unsupported {self.backend_label} transcription cache version: "
                    f"{cache_path}"
                )
            if payload.get("cache_identity") != expected_cache_identity:
                raise TranscriptionInferenceError(
                    f"Mismatched {self.backend_label} transcription cache identity: "
                    f"{cache_path}"
                )
            raw_segments = payload.get("segments")
            if not isinstance(raw_segments, list):
                raise TranscriptionInferenceError(
                    f"Malformed {self.backend_label} transcription cache payload: "
                    f"{cache_path}"
                )
            segments = [
                TranscribedSegment.model_validate(segment) for segment in raw_segments
            ]
        except TranscriptionError as exc:
            self._discard_invalid_entry(cache_path, exc)
            return None
        except (OSError, TypeError, ValueError) as exc:
            cache_error = TranscriptionInferenceError(
                f"Unable to read {self.backend_label} transcription cache "
                f"{cache_path}: {exc}"
            )
            self._discard_invalid_entry(cache_path, cache_error)
            return None

        cache_path.touch()
        logger.info(
            f"Loaded {self.backend_label} transcription from cache: {cache_path}"
        )
        return cache_path, segments

    def remove(self, audio: AudioSegment, cache_identity: CacheIdentity) -> Path | None:
        """Remove a cached transcription.

        Arguments:
            audio: audio used to derive the cache key
            cache_identity: backend configuration identifying the output
        Returns:
            removed cache path, if present
        """
        cache_path = self.get_path(audio, cache_identity)
        if not remove_cache_artifact(cache_path):
            return None
        logger.info(f"Removed {self.backend_label} transcription cache: {cache_path}")
        return cache_path

    def save(
        self,
        audio: AudioSegment,
        cache_identity: CacheIdentity,
        segments: Sequence[TranscribedSegment],
    ) -> Path:
        """Save a transcription to the cache.

        Arguments:
            audio: audio used to derive the cache key
            cache_identity: backend configuration identifying the output
            segments: timestamped transcription segments to cache
        Returns:
            saved cache path
        """
        cache_path = self.get_path(audio, cache_identity)
        payload = {
            "cache_version": _CACHE_VERSION,
            "cache_identity": self._get_cache_identity(audio, cache_identity),
            "segments": [segment.model_dump() for segment in segments],
        }
        with open_atomic_text_file(cache_path) as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        self._refreshed_paths.add(cache_path)
        logger.info(f"Saved {self.backend_label} transcription to cache: {cache_path}")
        return cache_path

    def _discard_invalid_entry(self, cache_path: Path, error: Exception):
        """Discard an invalid transcription cache entry.

        Arguments:
            cache_path: invalid transcription cache path
            error: validation or loading error
        """
        remove_cache_artifact(cache_path)
        logger.warning(
            f"Discarded invalid {self.backend_label} transcription cache "
            f"{cache_path}: {error}"
        )

    def _get_cache_identity(
        self, audio: AudioSegment, cache_identity: CacheIdentity
    ) -> CacheIdentity:
        """Get the complete cache identity.

        Arguments:
            audio: audio used to derive the cache identity
            cache_identity: backend configuration identifying the output
        Returns:
            complete cache identity
        """
        return {
            **cache_identity,
            "audio_channels": audio.channels,
            "audio_frame_rate": audio.frame_rate,
            "audio_sample_width": audio.sample_width,
            "backend": self.backend_name,
        }
