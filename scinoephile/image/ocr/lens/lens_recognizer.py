#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Google Lens OCR recognition engine."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from logging import getLogger
from pathlib import Path
from typing import TypedDict, cast, override

from PIL import Image

from scinoephile.common.validation import val_int
from scinoephile.core import Language
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.dependencies.ocr import import_chrome_lens_py

from .cache import LensCache

__all__ = ["LensRecognizer", "LensRecognizerKwargs"]

logger = getLogger(__name__)

_LENS_RETRY_DELAY_SECONDS = 1.5
_LENS_LANGUAGE_CODES = {
    Language.eng: "en",
    Language.yue_hans: "zh-CN",
    Language.yue_hant: "zh-TW",
    Language.zho_hans: "zh-CN",
    Language.zho_hant: "zh-TW",
}


class LensRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to LensRecognizer."""

    cache_root_path: Path | None
    """Root directory beneath which to cache OCR results, or None for default."""

    language: Language
    """Scinoephile language."""

    overwrite_cache: bool
    """Whether to replace matching OCR cache files."""

    retries: int
    """Google Lens OCR request attempts per uncached image."""


class _GoogleLensRequestError(RuntimeError):
    """Transient Google Lens request error returned as OCR text."""


class LensRecognizer:
    """Google Lens recognizer for image subtitles."""

    def __init__(
        self,
        *,
        cache_root_path: Path | None = None,
        language: Language = Language.eng,
        overwrite_cache: bool = False,
        retries: int = 3,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            language: Scinoephile language
            overwrite_cache: whether to replace matching OCR cache files
            retries: Google Lens OCR request attempts per uncached image
        """
        self._cache = LensCache(cache_root_path, overwrite_cache)
        try:
            self.language = language
            self.lens_language_code = _LENS_LANGUAGE_CODES[self.language]
        except (KeyError, ValueError) as exc:
            raise ValueError(f"{language} is not supported by Google Lens OCR") from exc
        self.retries = val_int(retries, min_value=1)

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"cache_root_path={self._cache.cache_root_path!r}, "
            f"language={self.language!r}, "
            f"overwrite_cache={self._cache.overwrite!r}, "
            f"retries={self.retries!r})"
        )

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        cache_identity: CacheIdentity = {"language": self.lens_language_code}
        if (lines := self._cache.load(image, cache_identity)) is not None:
            return self._format_lens_lines(lines)

        self._raise_if_running_loop()
        lines = self._recognize_image_uncached(image)
        self._cache.save(image, cache_identity, lines)
        return self._format_lens_lines(lines)

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
            if stripped.casefold() == "No OCR text found.".casefold():
                continue
            if (
                "Request error (possibly proxy-related)".casefold()
                in stripped.casefold()
            ):
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
    def _format_lens_lines(lines: list[str]) -> str:
        """Format normalized Google Lens OCR lines as subtitle text.

        Arguments:
            lines: normalized Google Lens OCR lines
        Returns:
            subtitle text
        """
        return LensRecognizer._clean_text("\n".join(lines))

    @staticmethod
    def _normalize_lens_result(result: object) -> list[str]:
        """Normalize raw Google Lens OCR result into recognized lines.

        Arguments:
            result: raw chrome-lens-py result
        Returns:
            normalized OCR lines
        """
        line_blocks = LensRecognizer._get_result_value(result, "line_blocks")
        if isinstance(line_blocks, list | tuple):
            lines = []
            for block in line_blocks:
                text = LensRecognizer._get_result_value(block, "text")
                if isinstance(text, str):
                    lines.append(text)
            if lines:
                return lines

        ocr_text = LensRecognizer._get_result_value(result, "ocr_text")
        if isinstance(ocr_text, str):
            return ocr_text.splitlines()
        return []

    @staticmethod
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

    @staticmethod
    def _raise_if_running_loop():
        """Raise if synchronous uncached recognition is called from an event loop.

        Raises:
            RuntimeError: if an asyncio event loop is already running
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return
        raise RuntimeError(
            "LensRecognizer cannot run uncached Google Lens OCR from an "
            "active asyncio event loop."
        )

    def _recognize_image_uncached(self, image: Image.Image) -> list[str]:
        """Recognize uncached image text through chrome-lens-py.

        Arguments:
            image: input image
        Returns:
            normalized OCR lines
        Raises:
            RuntimeError: if Google Lens returns request-error text
        """
        chrome_lens_py = import_chrome_lens_py()
        api = chrome_lens_py.LensAPI()

        async def recognize() -> list[str]:
            """Run Google Lens OCR retries in one event loop."""
            for attempt in range(1, self.retries + 1):
                try:
                    result = await api.process_image(
                        image_path=image,
                        ocr_language=self.lens_language_code,
                        ocr_preserve_line_breaks=True,
                        output_format="lines",
                    )
                    lines = self._normalize_lens_result(result)
                    self._raise_if_request_error(lines)
                except (chrome_lens_py.LensAPIError, _GoogleLensRequestError) as exc:
                    if attempt == self.retries:
                        raise
                    logger.warning(
                        f"Google Lens OCR attempt {attempt} of {self.retries} "
                        f"failed; retrying: {exc}"
                    )
                    await asyncio.sleep(_LENS_RETRY_DELAY_SECONDS)
                else:
                    return lines

            raise RuntimeError("Google Lens OCR retry loop exhausted without an error")

        return asyncio.run(recognize())

    @staticmethod
    def _raise_if_request_error(lines: list[str]):
        """Raise if normalized lines contain a Google Lens request error.

        Arguments:
            lines: normalized Google Lens OCR lines
        Raises:
            RuntimeError: if Google Lens returned a request error as OCR text
        """
        for line in lines:
            if "Request error (possibly proxy-related)".casefold() in line.casefold():
                raise _GoogleLensRequestError(f"Google Lens request error: {line}")
