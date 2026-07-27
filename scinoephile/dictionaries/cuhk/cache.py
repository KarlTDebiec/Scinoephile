#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK HTTP response cache."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from scinoephile.common.file import open_atomic_text_file
from scinoephile.common.validation import val_child_path, val_output_dir_path
from scinoephile.core.paths import get_runtime_cache_root_path

__all__ = ["CuhkResponseCache"]

logger = getLogger(__name__)

_CACHE_VERSION = 1
"""Current CUHK response cache version."""


class CuhkResponseCache:
    """Caches CUHK HTTP response bodies."""

    def __init__(
        self,
        cache_root_path: Path | None,
        cache_dir_name: str,
        overwrite: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            cache_dir_name: cache subdirectory name
            overwrite: whether to replace matching cache files
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which CUHK responses are cached."""
        self.cache_dir_path = val_output_dir_path(self.cache_root_path / cache_dir_name)
        """Directory in which cached CUHK responses are stored."""

        self.overwrite = overwrite
        """Whether matching cache files should be replaced."""

        self._refreshed_paths: set[Path] = set()
        """Cache paths refreshed by this cache instance."""

    def get_path(self, stem: str) -> Path:
        """Get a versioned response cache path.

        Arguments:
            stem: safe filename stem identifying the response
        Returns:
            response cache path
        """
        validated_stem = val_child_path(self.cache_dir_path, stem).name
        return (
            self.cache_dir_path
            / f"{validated_stem}-v{_CACHE_VERSION}"
            / f"{validated_stem}.html"
        )

    def get_stems(self) -> list[str]:
        """Get all response stems for the current cache version.

        Returns:
            sorted response cache stems
        """
        return [
            cache_path.stem
            for cache_path in sorted(
                self.cache_dir_path.glob(f"*-v{_CACHE_VERSION}/*.html")
            )
        ]

    def load(self, stem: str) -> str | None:
        """Load a cached response body.

        Invalid cache files are discarded and treated as cache misses.

        Arguments:
            stem: safe filename stem identifying the response
        Returns:
            cached response body, if present and valid
        """
        cache_path = self.get_path(stem)
        if self.overwrite and cache_path not in self._refreshed_paths:
            self._refreshed_paths.add(cache_path)
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"Removed CUHK response cache: {cache_path}")
        if not cache_path.exists():
            return None

        try:
            contents = cache_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            cache_path.unlink(missing_ok=True)
            logger.warning(f"Discarded invalid CUHK response cache {cache_path}: {exc}")
            return None

        cache_path.touch()
        logger.info(f"Loaded CUHK response from cache: {cache_path}")
        return contents

    def remove(self, stem: str) -> Path | None:
        """Remove a cached response body.

        Arguments:
            stem: safe filename stem identifying the response
        Returns:
            removed cache path, if present
        """
        cache_path = self.get_path(stem)
        if not cache_path.exists():
            return None
        cache_path.unlink()
        logger.info(f"Removed CUHK response cache: {cache_path}")
        return cache_path

    def save(self, stem: str, contents: str) -> Path:
        """Save a response body to the cache.

        Arguments:
            stem: safe filename stem identifying the response
            contents: response body
        Returns:
            saved cache path
        """
        cache_path = self.get_path(stem)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open_atomic_text_file(cache_path) as cache_file:
            cache_file.write(contents)
        self._refreshed_paths.add(cache_path)
        logger.info(f"Saved CUHK response to cache: {cache_path}")
        return cache_path
