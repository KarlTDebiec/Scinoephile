#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract legacy data cache."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.cache.artifact import remove_cache_artifact
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_root_path
from scinoephile.image.cache_namespace import ImageCacheNamespace

__all__ = ["TESSERACT_LEGACY_DATA_REVISION", "TesseractLegacyDataCache"]

logger = getLogger(__name__)

TESSERACT_LEGACY_DATA_REVISION = "ced78752cc61322fb554c280d13360b35b8684e4"
"""Pinned tessdata source revision."""

_CACHE_VERSION = 2
"""Current Tesseract legacy data cache version."""


class TesseractLegacyDataCache:
    """Caches legacy-capable Tesseract traineddata files."""

    def __init__(
        self,
        cache_root_path: Path | None = None,
        source_revision: str = TESSERACT_LEGACY_DATA_REVISION,
        overwrite: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            source_revision: pinned tessdata source revision
            overwrite: whether to replace matching cache files
        Raises:
            ValueError: if source_revision is not a simple path segment
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which traineddata files are cached."""
        self.cache_dir_path = (
            ImageCacheNamespace.OCR_TESSERACT_LEGACY_DATA.get_dir_path(
                self.cache_root_path
            )
        )
        """Directory in which legacy-capable traineddata files are stored."""

        if not source_revision or Path(source_revision).name != source_revision:
            raise ValueError("Tesseract source revision must be a simple path segment")
        self.source_revision = source_revision
        """Pinned tessdata source revision."""

        self.overwrite = overwrite
        """Whether matching cache files should be replaced."""

        self._refreshed_paths: set[Path] = set()
        """Cache paths refreshed by this cache instance."""

    def get_path(self, language_code: str) -> Path:
        """Get the cache path for one Tesseract language.

        Arguments:
            language_code: Tesseract language code
        Returns:
            traineddata cache path
        Raises:
            ValueError: if the language code is not a simple filename stem
        """
        if not language_code or Path(language_code).name != language_code:
            raise ValueError("Tesseract language code must be a simple filename stem")
        return (
            self.cache_dir_path
            / f"{language_code}-{self.source_revision}-v{_CACHE_VERSION}"
            / f"{language_code}.traineddata"
        )

    def load(self, language_code: str) -> Path | None:
        """Load a cached traineddata path.

        Arguments:
            language_code: Tesseract language code
        Returns:
            cached traineddata path, if present
        """
        traineddata_path = self.get_path(language_code)
        if self.overwrite and traineddata_path not in self._refreshed_paths:
            self._refreshed_paths.add(traineddata_path)
            if remove_cache_artifact(traineddata_path):
                logger.info(
                    f"Removed Tesseract legacy traineddata cache: {traineddata_path}"
                )
        if (
            not traineddata_path.is_file()
            or traineddata_path.is_symlink()
            or traineddata_path.stat().st_size == 0
        ):
            if remove_cache_artifact(traineddata_path):
                logger.warning(
                    f"Discarded invalid Tesseract legacy traineddata cache: "
                    f"{traineddata_path}"
                )
            return None
        traineddata_path.touch()
        logger.info(
            f"Loaded Tesseract legacy traineddata from cache: {traineddata_path}"
        )
        return traineddata_path

    def save(self, language_code: str, contents: bytes) -> Path:
        """Save legacy-capable traineddata to the cache.

        Arguments:
            language_code: Tesseract language code
            contents: traineddata file contents
        Returns:
            saved traineddata path
        Raises:
            ScinoephileError: if the traineddata cache cannot be written
            ValueError: if the traineddata contents are empty
        """
        if not contents:
            raise ValueError("Tesseract legacy traineddata cannot be empty.")
        traineddata_path = self.get_path(language_code)
        try:
            traineddata_path.parent.mkdir(parents=True, exist_ok=True)
            with TemporaryDirectory(
                dir=traineddata_path.parent, prefix=f".{traineddata_path.name}-"
            ) as temp_dir:
                staging_path = Path(temp_dir) / traineddata_path.name
                staging_path.write_bytes(contents)
                staging_path.replace(traineddata_path)
        except OSError as exc:
            raise ScinoephileError(
                f"Unable to write Tesseract legacy traineddata cache "
                f"{traineddata_path}: {exc}"
            ) from exc
        self._refreshed_paths.add(traineddata_path)
        logger.info(f"Saved Tesseract legacy traineddata to cache: {traineddata_path}")
        return traineddata_path
