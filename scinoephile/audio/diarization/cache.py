#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache for source-wide speaker diarization results."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.common.file import open_atomic_text_file
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.cache.artifact import remove_cache_artifact
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.paths import get_runtime_cache_root_path

from .models import SpeakerDiarizationResult

__all__ = ["SpeakerDiarizationCache"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_CACHE_VERSION = 2
"""Current speaker diarization cache version."""


class SpeakerDiarizationCache:
    """Cache source-wide speaker diarization by audio and pipeline identity."""

    def __init__(self, cache_root_path: Path | None, overwrite: bool = False):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            overwrite: whether to replace a matching cache entry
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which diarization is cached."""
        self.cache_dir_path = AudioCacheNamespace.DIARIZATION.get_dir_path(
            self.cache_root_path
        )
        """Directory in which source-wide diarization results are cached."""
        self.overwrite = overwrite
        """Whether matching cache entries should be replaced."""
        self._refreshed_paths: set[Path] = set()
        """Cache paths refreshed by this cache instance."""

    def get_path(self, audio: AudioSegment, cache_identity: CacheIdentity) -> Path:
        """Get the cache path for audio and pipeline configuration.

        Arguments:
            audio: complete source audio used to derive the cache key
            cache_identity: pipeline configuration identifying the output
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
    ) -> SpeakerDiarizationResult | None:
        """Load a cached source-wide speaker diarization result.

        Arguments:
            audio: complete source audio used to derive the cache key
            cache_identity: pipeline configuration identifying the output
        Returns:
            validated diarization result, if present

        Raises:
            ValueError: if a value is invalid
        """
        cache_path = self.get_path(audio, cache_identity)
        if self.overwrite and cache_path not in self._refreshed_paths:
            self._refreshed_paths.add(cache_path)
            if remove_cache_artifact(cache_path):
                logger.info(f"Removed speaker diarization cache: {cache_path}")
        if not cache_path.is_file() or cache_path.is_symlink():
            if remove_cache_artifact(cache_path):
                logger.warning(
                    f"Discarded invalid speaker diarization cache: {cache_path}"
                )
            return None

        expected_cache_identity = self._get_cache_identity(audio, cache_identity)
        try:
            with cache_path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            if not isinstance(payload, Mapping):
                raise ValueError("cache payload must be a mapping")
            if payload.get("cache_version") != _CACHE_VERSION:
                raise ValueError("cache version is unsupported")
            if payload.get("cache_identity") != expected_cache_identity:
                raise ValueError("cache identity does not match")
            result = SpeakerDiarizationResult.model_validate(payload.get("result"))
        except (OSError, TypeError, ValueError) as exc:
            remove_cache_artifact(cache_path)
            logger.warning(
                f"Discarded invalid speaker diarization cache {cache_path}: {exc}"
            )
            return None

        cache_path.touch()
        logger.info(f"Loaded speaker diarization from cache: {cache_path}")
        return result

    def save(
        self,
        audio: AudioSegment,
        cache_identity: CacheIdentity,
        result: SpeakerDiarizationResult,
    ) -> Path:
        """Save a source-wide speaker diarization result.

        Arguments:
            audio: complete source audio used to derive the cache key
            cache_identity: pipeline configuration identifying the output
            result: overlap-aware and exclusive speaker turns
        Returns:
            saved cache path
        """
        cache_path = self.get_path(audio, cache_identity)
        payload = {
            "cache_version": _CACHE_VERSION,
            "cache_identity": self._get_cache_identity(audio, cache_identity),
            "result": result.model_dump(mode="json"),
        }
        with open_atomic_text_file(cache_path) as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        self._refreshed_paths.add(cache_path)
        logger.info(f"Saved speaker diarization to cache: {cache_path}")
        return cache_path

    @staticmethod
    def _get_cache_identity(
        audio: AudioSegment, cache_identity: CacheIdentity
    ) -> CacheIdentity:
        """Get the complete cache identity.

        Arguments:
            audio: complete source audio used to derive the cache identity
            cache_identity: pipeline configuration identifying the output
        Returns:
            complete cache identity
        """
        return {
            **cache_identity,
            "audio_channels": audio.channels,
            "audio_frame_rate": audio.frame_rate,
            "audio_sample_width": audio.sample_width,
        }
