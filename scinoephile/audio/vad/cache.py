#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Persistent cache for frame-level voice activity traces."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING
from zipfile import BadZipFile

import numpy as np

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.cache.artifact import remove_cache_artifact
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.paths import get_runtime_cache_root_path

from .trace import VoiceActivityTrace

__all__ = ["VoiceActivityCache"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_CACHE_VERSION = 2
"""Current voice activity trace cache version."""


class VoiceActivityCache:
    """Cache frame-level voice activity traces by audio and model identity."""

    def __init__(self, cache_root_path: Path | None, overwrite: bool = False):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            overwrite: whether to replace a matching cache entry
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which voice activity is cached."""
        self.cache_dir_path = AudioCacheNamespace.VAD.get_dir_path(self.cache_root_path)
        """Directory in which voice activity traces are cached."""
        self.overwrite = overwrite
        """Whether matching cache entries should be replaced."""
        self._refreshed_paths: set[Path] = set()
        """Cache paths refreshed by this cache instance."""

    def get_path(self, audio: AudioSegment, cache_identity: CacheIdentity) -> Path:
        """Get the cache path for audio and model configuration.

        Arguments:
            audio: source audio used to derive the cache key
            cache_identity: model configuration identifying the score trace
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
        return self.cache_dir_path / f"{cache_hash.hexdigest()}.npz"

    def load(
        self, audio: AudioSegment, cache_identity: CacheIdentity
    ) -> VoiceActivityTrace | None:
        """Load a cached voice activity trace.

        Arguments:
            audio: source audio used to derive the cache key
            cache_identity: model configuration identifying the score trace
        Returns:
            validated trace, if present

        Raises:
            ValueError: if a value is invalid
        """
        cache_path = self.get_path(audio, cache_identity)
        if self.overwrite and cache_path not in self._refreshed_paths:
            self._refreshed_paths.add(cache_path)
            if remove_cache_artifact(cache_path):
                logger.info(f"Removed voice activity trace cache: {cache_path}")
        if not cache_path.is_file() or cache_path.is_symlink():
            if remove_cache_artifact(cache_path):
                logger.warning(
                    f"Discarded invalid voice activity trace cache: {cache_path}"
                )
            return None

        expected_cache_identity = self._get_cache_identity(audio, cache_identity)
        try:
            with np.load(cache_path, allow_pickle=False) as payload:
                raw_cache_identity = payload["cache_identity"].item()
                if not isinstance(raw_cache_identity, str):
                    raise ValueError("cache identity must be serialized text")
                if json.loads(raw_cache_identity) != expected_cache_identity:
                    raise ValueError("cache identity does not match")
                trace = VoiceActivityTrace(
                    payload["scores"],
                    start_ms=float(payload["start_ms"]),
                    step_ms=float(payload["step_ms"]),
                    duration_ms=int(payload["duration_ms"]),
                )
                if trace.duration_ms != len(audio):
                    raise ValueError("cache duration does not match source audio")
        except (BadZipFile, KeyError, OSError, TypeError, ValueError) as exc:
            remove_cache_artifact(cache_path)
            logger.warning(
                f"Discarded invalid voice activity trace cache {cache_path}: {exc}"
            )
            return None

        cache_path.touch()
        logger.info(f"Loaded voice activity trace from cache: {cache_path}")
        return trace

    def remove(self, audio: AudioSegment, cache_identity: CacheIdentity) -> Path | None:
        """Remove a cached voice activity trace.

        Arguments:
            audio: source audio used to derive the cache key
            cache_identity: model configuration identifying the score trace
        Returns:
            removed cache path, if present
        """
        cache_path = self.get_path(audio, cache_identity)
        if not remove_cache_artifact(cache_path):
            return None
        logger.info(f"Removed voice activity trace cache: {cache_path}")
        return cache_path

    def save(
        self,
        audio: AudioSegment,
        cache_identity: CacheIdentity,
        trace: VoiceActivityTrace,
    ) -> Path:
        """Save a voice activity trace.

        Arguments:
            audio: source audio used to derive the cache key
            cache_identity: model configuration identifying the score trace
            trace: frame-level voice activity scores
        Returns:
            saved cache path
        Raises:
            ValueError: if the trace duration does not match the source audio
        """
        if trace.duration_ms != len(audio):
            raise ValueError(
                "Voice activity trace duration does not match source audio."
            )
        cache_path = self.get_path(audio, cache_identity)
        serialized_cache_identity = json.dumps(
            self._get_cache_identity(audio, cache_identity),
            ensure_ascii=False,
            sort_keys=True,
        )
        with TemporaryDirectory(
            dir=cache_path.parent, prefix=f".{cache_path.stem}-"
        ) as temp_dir:
            staging_path = Path(temp_dir) / cache_path.name
            np.savez_compressed(
                staging_path,
                cache_identity=np.asarray(serialized_cache_identity),
                scores=trace.scores,
                start_ms=np.asarray(trace.start_ms),
                step_ms=np.asarray(trace.step_ms),
                duration_ms=np.asarray(trace.duration_ms),
            )
            staging_path.replace(cache_path)
        self._refreshed_paths.add(cache_path)
        logger.info(f"Saved voice activity trace to cache: {cache_path}")
        return cache_path

    @staticmethod
    def _get_cache_identity(
        audio: AudioSegment, cache_identity: CacheIdentity
    ) -> CacheIdentity:
        """Get the complete cache identity.

        Arguments:
            audio: source audio used to derive the cache identity
            cache_identity: model configuration identifying the score trace
        Returns:
            complete cache identity
        """
        return {
            **cache_identity,
            "audio_channels": audio.channels,
            "audio_frame_rate": audio.frame_rate,
            "audio_sample_width": audio.sample_width,
            "cache_version": _CACHE_VERSION,
        }
