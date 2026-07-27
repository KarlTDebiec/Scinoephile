#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract legacy data cache."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_root_path

__all__ = ["TesseractLegacyDataCache"]

logger = getLogger(__name__)


class TesseractLegacyDataCache:
    """Caches legacy-capable Tesseract traineddata files."""

    def __init__(self, cache_root_path: Path | None = None):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
        """
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        self.cache_root_path = val_output_dir_path(cache_root_path)
        """Root directory beneath which traineddata files are cached."""
        self.cache_dir_path = val_output_dir_path(
            self.cache_root_path / "tesseract-legacy-data"
        )
        """Directory in which legacy-capable traineddata files are stored."""

    def load(self, language_code: str) -> Path | None:
        """Load a cached traineddata path.

        Arguments:
            language_code: Tesseract language code
        Returns:
            cached traineddata path, if present
        """
        traineddata_path = self._get_path(language_code)
        if not traineddata_path.is_file():
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
        """
        traineddata_path = self._get_path(language_code)
        try:
            with TemporaryDirectory(
                dir=traineddata_path.parent,
                prefix=f".{traineddata_path.name}-",
            ) as temp_dir:
                staging_path = Path(temp_dir) / traineddata_path.name
                staging_path.write_bytes(contents)
                staging_path.replace(traineddata_path)
        except OSError as exc:
            raise ScinoephileError(
                f"Unable to write Tesseract legacy traineddata cache "
                f"{traineddata_path}: {exc}"
            ) from exc
        logger.info(f"Saved Tesseract legacy traineddata to cache: {traineddata_path}")
        return traineddata_path

    def _get_path(self, language_code: str) -> Path:
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
        return self.cache_dir_path / f"{language_code}.traineddata"
