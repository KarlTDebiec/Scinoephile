#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Google Lens OCR recognition engine."""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Mapping
from logging import getLogger
from pathlib import Path
from typing import Any, cast, override

from PIL import Image

from scinoephile.common.validation import val_output_dir_path

__all__ = ["GoogleLensRecognizer"]

logger = getLogger(__name__)
LensAPI: Any | None = None

_NO_TEXT_MESSAGE = "No OCR text found."
_REQUEST_ERROR_MESSAGE = "Request error (possibly proxy-related)"


class GoogleLensRecognizer:
    """Google Lens recognizer for image subtitles."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        cache_dir_path: Path | None = None,
        client_region: str | None = None,
        client_time_zone: str | None = None,
        language: str = "en",
        max_concurrent: int = 5,
        proxy: str | None = None,
        timeout: int = 60,
    ):
        """Initialize.

        Arguments:
            api_key: optional Google Lens API key override
            cache_dir_path: directory in which to cache OCR results
            client_region: optional Google Lens client region
            client_time_zone: optional Google Lens client time zone
            language: Google Lens OCR language code
            max_concurrent: maximum concurrent Lens requests
            proxy: optional proxy URL
            timeout: request timeout in seconds
        """
        self.api_key = api_key
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)
        self.client_region = client_region
        self.client_time_zone = client_time_zone
        self.language = language
        self.max_concurrent = max_concurrent
        self.proxy = proxy
        self.timeout = timeout

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"api_key={self.api_key!r}, "
            f"cache_dir_path={self.cache_dir_path!r}, "
            f"client_region={self.client_region!r}, "
            f"client_time_zone={self.client_time_zone!r}, "
            f"language={self.language!r}, "
            f"max_concurrent={self.max_concurrent!r}, "
            f"proxy={self.proxy!r}, "
            f"timeout={self.timeout!r})"
        )

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        if (cache_path := self._get_cache_path(image)) is not None:
            if cache_path.exists():
                text = self._load_text(cache_path)
                cache_path.touch()
                logger.info(f"Loaded Google Lens OCR result from cache: {cache_path}")
                return text

            text = asyncio.run(self._recognize_image_uncached(image))
            self._save_text(text, cache_path)
            logger.info(f"Saved Google Lens OCR result to cache: {cache_path}")
            return text

        return asyncio.run(self._recognize_image_uncached(image))

    def recognize_images(self, images: list[Image.Image]) -> list[str]:
        """Recognize text from multiple images.

        Arguments:
            images: input images
        Returns:
            recognized text for each input image
        """
        return [self.recognize_image(image) for image in images]

    def _get_cache_path(self, image: Image.Image) -> Path | None:
        """Get cache path based on image data and OCR configuration.

        Arguments:
            image: image used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None

        image_bytes = image.tobytes()
        image_sha256 = hashlib.sha256(image_bytes).hexdigest()
        cache_key = (
            f"{image_sha256}_{image.mode}_{image.size}_{self.language}_"
            f"{self.client_region}_{self.client_time_zone}_chrome-lens-py"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean Google Lens OCR text using SubtitleEdit line rules.

        Arguments:
            text: raw recognized text
        Returns:
            cleaned recognized text
        """
        lines = []
        for line in text.strip().splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.casefold() == _NO_TEXT_MESSAGE.casefold():
                continue
            if _REQUEST_ERROR_MESSAGE.casefold() in stripped.casefold():
                continue
            lines.append(stripped)

        index = 0
        while index < len(lines):
            if lines[index] == "-" and index + 1 < len(lines):
                lines[index] = f"- {lines[index + 1]}"
                del lines[index + 1]
                continue
            index += 1

        index = 0
        while index < len(lines):
            if (
                lines[index] == "..."
                and index - 1 >= 0
                and not lines[index - 1].endswith(".")
            ):
                lines[index - 1] = f"{lines[index - 1]} ..."
                del lines[index]
                continue
            if lines[index] == "..." and index + 1 < len(lines):
                lines[index] = f"... {lines[index + 1]}"
                del lines[index + 1]
                continue
            index += 1

        return "\n".join(lines).strip()

    @staticmethod
    def _extract_text(result: object) -> str:
        """Extract subtitle text from a chrome-lens-py result.

        Arguments:
            result: chrome-lens-py result
        Returns:
            recognized text
        """
        line_blocks = _get_result_value(result, "line_blocks")
        if isinstance(line_blocks, list | tuple) and line_blocks:
            lines = []
            for block in line_blocks:
                text = _get_result_value(block, "text")
                if isinstance(text, str):
                    lines.append(text)
            if lines:
                return "\n".join(lines)

        ocr_text = _get_result_value(result, "ocr_text")
        if isinstance(ocr_text, str):
            return ocr_text
        return ""

    @staticmethod
    def _get_lens_api_class() -> Any:
        """Import chrome-lens-py on demand.

        Returns:
            chrome-lens-py LensAPI class
        Raises:
            ImportError: if chrome-lens-py is not installed
        """
        global LensAPI  # noqa: PLW0603
        if LensAPI is None:
            try:
                from chrome_lens_py import (  # ty: ignore[unresolved-import]  # noqa: PLC0415
                    LensAPI as ImportedLensAPI,
                )
            except ImportError as exc:
                raise ImportError(
                    "Google Lens OCR support requires chrome-lens-py. Install "
                    "scinoephile with the 'ocr' extra."
                ) from exc
            LensAPI = ImportedLensAPI
        return LensAPI

    @staticmethod
    def _load_text(cache_path: Path) -> str:
        """Load cached Google Lens OCR text.

        Arguments:
            cache_path: cache file path
        Returns:
            recognized text
        """
        with cache_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return str(data["text"])

    async def _recognize_image_uncached(self, image: Image.Image) -> str:
        """Recognize uncached image text through chrome-lens-py.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        lens_api_cls = self._get_lens_api_class()
        lens_api_kwargs: dict[str, object] = {
            "max_concurrent": self.max_concurrent,
            "timeout": self.timeout,
        }
        if self.api_key is not None:
            lens_api_kwargs["api_key"] = self.api_key
        if self.client_region is not None:
            lens_api_kwargs["client_region"] = self.client_region
        if self.client_time_zone is not None:
            lens_api_kwargs["client_time_zone"] = self.client_time_zone
        if self.proxy is not None:
            lens_api_kwargs["proxy"] = self.proxy

        api = lens_api_cls(**lens_api_kwargs)
        result = await api.process_image(
            image_path=image,
            ocr_language=self.language,
            ocr_preserve_line_breaks=True,
            output_format="lines",
        )
        return self._clean_text(self._extract_text(result))

    @staticmethod
    def _save_text(text: str, cache_path: Path):
        """Save Google Lens OCR text to cache.

        Arguments:
            text: recognized text
            cache_path: cache file path
        """
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump({"text": text}, file, ensure_ascii=False)


def _get_result_value(result: object, key: str) -> object:
    """Get a value from a dict-like or object-like result.

    Arguments:
        result: result object
        key: value key or attribute name
    Returns:
        value if present
    """
    if isinstance(result, Mapping):
        return cast(Mapping[str, object], result).get(key)
    return getattr(result, key, None)
