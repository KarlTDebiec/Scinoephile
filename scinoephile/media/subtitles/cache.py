#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream cache."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path
from shutil import rmtree

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.media import SubtitleStream
from scinoephile.core.paths import get_runtime_cache_root_path
from scinoephile.image.subtitles import ImageSeries
from scinoephile.media.cache_namespace import MediaCacheNamespace

__all__ = ["SubtitleCache"]

logger = getLogger(__name__)

_CACHE_VERSION = 1
"""Current subtitle stream cache version."""


class SubtitleCache:
    """Cache of subtitle streams extracted from media."""

    def __init__(self, cache_root_path: Path | None = None, overwrite: bool = False):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            overwrite: whether to replace matching cached subtitle artifacts
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which subtitle artifacts are cached."""

        self.cache_dir_path = val_output_dir_path(
            MediaCacheNamespace.SUBTITLES.get_dir_path(self.cache_root_path)
        )
        """Directory in which cached subtitle streams are stored."""

        self.overwrite = overwrite
        """Whether matching cached subtitle artifacts should be replaced."""

        self._refreshed_paths: set[Path] = set()
        """Cache paths refreshed by this cache instance."""

    def get_image_series_dir_path(
        self, infile_path: Path, stream: SubtitleStream
    ) -> Path:
        """Get the cache directory for a rendered image subtitle series.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
        Returns:
            image subtitle series cache directory
        """
        return self.get_path(infile_path, stream).parent / "image-series"

    def get_path(self, infile_path: Path, stream: SubtitleStream) -> Path:
        """Get the cache path for an extracted subtitle stream.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
        Returns:
            subtitle stream cache path
        """
        infile_path = infile_path.resolve()
        stat = infile_path.stat()
        payload = {
            "cache_version": _CACHE_VERSION,
            "path": str(infile_path),
            "size": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
            "stream_index": stream.index,
            "codec_name": stream.codec_name,
        }
        encoded_payload = json.dumps(payload, sort_keys=True).encode("utf-8")
        cache_key = hashlib.sha256(encoded_payload).hexdigest()
        return self.cache_dir_path / cache_key / f"{stream.index}.{stream.extension}"

    def load(self, infile_path: Path, stream: SubtitleStream) -> Path | None:
        """Load a cached subtitle stream path.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
        Returns:
            cached subtitle stream path, if present
        """
        stream_path = self.get_path(infile_path, stream)
        self._remove_for_overwrite(stream_path, "subtitle stream")
        if stream_path.is_file():
            stream_path.touch()
            logger.info(f"Loaded subtitle stream from cache: {stream_path}")
            return stream_path
        if stream_path.exists() or stream_path.is_symlink():
            self._remove_artifact(stream_path)
            logger.warning(f"Discarded invalid subtitle stream cache: {stream_path}")
        return None

    def load_image_series(
        self, infile_path: Path, stream: SubtitleStream
    ) -> Path | None:
        """Load a cached image subtitle series directory.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
        Returns:
            cached image subtitle series directory, if present
        """
        image_dir_path = self.get_image_series_dir_path(infile_path, stream)
        index_path = image_dir_path / "index.html"
        self._remove_for_overwrite(image_dir_path, "image subtitle series")
        if index_path.is_file():
            index_path.touch()
            logger.info(f"Loaded image subtitle series from cache: {image_dir_path}")
            return image_dir_path
        if image_dir_path.exists() or image_dir_path.is_symlink():
            self._remove_artifact(image_dir_path)
            logger.warning(
                f"Discarded invalid image subtitle series cache: {image_dir_path}"
            )
        return None

    def remove(self, infile_path: Path, stream: SubtitleStream) -> Path | None:
        """Remove a cached subtitle stream.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
        Returns:
            removed cache path, if present
        """
        stream_path = self.get_path(infile_path, stream)
        if not stream_path.exists() and not stream_path.is_symlink():
            return None
        self._remove_artifact(stream_path)
        logger.info(f"Removed subtitle stream cache: {stream_path}")
        return stream_path

    def remove_image_series(
        self, infile_path: Path, stream: SubtitleStream
    ) -> Path | None:
        """Remove a cached image subtitle series.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
        Returns:
            removed cache directory, if present
        """
        image_dir_path = self.get_image_series_dir_path(infile_path, stream)
        if not image_dir_path.exists() and not image_dir_path.is_symlink():
            return None
        self._remove_artifact(image_dir_path)
        logger.info(f"Removed image subtitle series cache: {image_dir_path}")
        return image_dir_path

    def save(
        self, infile_path: Path, stream: SubtitleStream, staging_path: Path
    ) -> Path:
        """Save an extracted subtitle stream to the cache.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
            staging_path: staged subtitle stream file
        Returns:
            saved cache path
        """
        stream_path = self.get_path(infile_path, stream)
        stream_path.parent.mkdir(parents=True, exist_ok=True)
        staging_path.replace(stream_path)
        self._refreshed_paths.add(stream_path)
        logger.info(f"Saved subtitle stream to cache: {stream_path}")
        return stream_path

    def save_image_series(
        self, infile_path: Path, stream: SubtitleStream, image_series: ImageSeries
    ) -> Path:
        """Save a rendered image subtitle series to the cache.

        Arguments:
            infile_path: media input file
            stream: subtitle stream
            image_series: rendered image subtitle series
        Returns:
            saved cache directory
        """
        image_dir_path = self.get_image_series_dir_path(infile_path, stream)
        image_series.save(image_dir_path)
        self._refreshed_paths.add(image_dir_path)
        logger.info(f"Saved image subtitle series to cache: {image_dir_path}")
        return image_dir_path

    def _remove_for_overwrite(self, artifact_path: Path, label: str):
        """Remove a matching artifact once when overwrite is enabled.

        Arguments:
            artifact_path: cached artifact path
            label: artifact label used in logging
        """
        if not self.overwrite or artifact_path in self._refreshed_paths:
            return
        self._refreshed_paths.add(artifact_path)
        if not artifact_path.exists() and not artifact_path.is_symlink():
            return
        self._remove_artifact(artifact_path)
        logger.info(f"Removed {label} cache: {artifact_path}")

    @staticmethod
    def _remove_artifact(artifact_path: Path):
        """Remove a cached file, directory, or symbolic link.

        Arguments:
            artifact_path: cached artifact to remove
        """
        if artifact_path.is_dir() and not artifact_path.is_symlink():
            rmtree(artifact_path)
        else:
            artifact_path.unlink(missing_ok=True)
