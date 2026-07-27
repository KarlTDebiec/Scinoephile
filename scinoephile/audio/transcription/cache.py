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

from scinoephile.common.file import open_atomic_text_file
from scinoephile.common.validation import val_output_dir_path

from .exceptions import TranscriptionError, TranscriptionInferenceError
from .transcribed_segment import TranscribedSegment

__all__ = ["TranscriptionCache"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_CACHE_SCHEMA_VERSION = 1
"""Current transcription cache payload schema version."""


class TranscriptionCache:
    """Caches timestamped transcription output by audio and backend configuration."""

    def __init__(
        self,
        cache_root_path: Path | None,
        backend_name: str,
        backend_label: str,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None to disable
            backend_name: stable backend name stored in cache metadata
            backend_label: human-readable backend name used in log messages
        """
        self.backend_name = backend_name
        """Stable backend name stored in cache metadata."""
        self.backend_label = backend_label
        """Human-readable backend name used in log messages."""
        self.cache_dir_path = None
        """Directory in which cached transcriptions are stored."""
        if cache_root_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_root_path / backend_name)

    def get_path(
        self,
        audio: AudioSegment,
        backend_metadata: Mapping[str, object],
    ) -> Path | None:
        """Get the cache path for audio and backend configuration.

        Arguments:
            audio: audio used to derive the cache key
            backend_metadata: backend configuration identifying the output
        Returns:
            cache path, or None when caching is disabled
        """
        if self.cache_dir_path is None:
            return None

        cache_hash = hashlib.sha256(audio.raw_data)
        cache_hash.update(b"\0")
        cache_hash.update(
            json.dumps(
                self._get_metadata(audio, backend_metadata),
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        )
        return self.cache_dir_path / f"{cache_hash.hexdigest()}.json"

    def load(
        self,
        audio: AudioSegment,
        backend_metadata: Mapping[str, object],
    ) -> tuple[Path, list[TranscribedSegment]] | None:
        """Load a cached transcription.

        Arguments:
            audio: audio used to derive the cache key
            backend_metadata: backend configuration identifying the output
        Returns:
            cache path and cached segments, if present
        Raises:
            TranscriptionInferenceError: if the cache payload is malformed
        """
        cache_path = self.get_path(audio, backend_metadata)
        if cache_path is None or not cache_path.exists():
            return None

        expected_metadata = self._get_metadata(audio, backend_metadata)
        try:
            with cache_path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            if not isinstance(payload, Mapping):
                raise TranscriptionInferenceError(
                    f"Malformed {self.backend_label} transcription cache payload: "
                    f"{cache_path}"
                )
            if payload.get("schema_version") != _CACHE_SCHEMA_VERSION:
                raise TranscriptionInferenceError(
                    f"Unsupported {self.backend_label} transcription cache schema: "
                    f"{cache_path}"
                )
            if payload.get("metadata") != expected_metadata:
                raise TranscriptionInferenceError(
                    f"Mismatched {self.backend_label} transcription cache metadata: "
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
        except TranscriptionError:
            raise
        except (OSError, TypeError, ValueError) as exc:
            raise TranscriptionInferenceError(
                f"Unable to read {self.backend_label} transcription cache "
                f"{cache_path}: {exc}"
            ) from exc

        cache_path.touch()
        logger.info(
            f"Loaded {self.backend_label} transcription from cache: {cache_path}"
        )
        return cache_path, segments

    def remove(
        self,
        audio: AudioSegment,
        backend_metadata: Mapping[str, object],
    ) -> Path | None:
        """Remove a cached transcription.

        Arguments:
            audio: audio used to derive the cache key
            backend_metadata: backend configuration identifying the output
        Returns:
            removed cache path, if present
        """
        cache_path = self.get_path(audio, backend_metadata)
        if cache_path is None or not cache_path.exists():
            return None

        cache_path.unlink()
        logger.info(f"Removed {self.backend_label} transcription cache: {cache_path}")
        return cache_path

    def save(
        self,
        audio: AudioSegment,
        backend_metadata: Mapping[str, object],
        segments: Sequence[TranscribedSegment],
    ) -> Path | None:
        """Save a transcription to the cache.

        Arguments:
            audio: audio used to derive the cache key
            backend_metadata: backend configuration identifying the output
            segments: timestamped transcription segments to cache
        Returns:
            saved cache path, or None when caching is disabled
        """
        cache_path = self.get_path(audio, backend_metadata)
        if cache_path is None:
            return None

        payload = {
            "schema_version": _CACHE_SCHEMA_VERSION,
            "metadata": self._get_metadata(audio, backend_metadata),
            "segments": [segment.model_dump() for segment in segments],
        }
        with open_atomic_text_file(cache_path) as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        logger.info(f"Saved {self.backend_label} transcription to cache: {cache_path}")
        return cache_path

    def _get_metadata(
        self,
        audio: AudioSegment,
        backend_metadata: Mapping[str, object],
    ) -> dict[str, object]:
        """Get complete cache identity metadata.

        Arguments:
            audio: audio used to derive the cache identity
            backend_metadata: backend configuration identifying the output
        Returns:
            complete cache identity metadata
        """
        return {
            **backend_metadata,
            "audio_channels": audio.channels,
            "audio_frame_rate": audio.frame_rate,
            "audio_sample_width": audio.sample_width,
            "backend": self.backend_name,
        }
