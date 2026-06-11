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
from typing import Any, TypedDict, cast, override

from PIL import Image

from scinoephile.common.validation import val_int, val_output_dir_path
from scinoephile.core import Language

__all__ = [
    "LensRecognizer",
    "LensRecognizerKwargs",
]

logger = getLogger(__name__)

_OCR_EXTRA_MESSAGE = (
    "Google Lens OCR support requires optional OCR dependencies. "
    "Install scinoephile with the 'ocr' extra."
)
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

    cache_dir_path: Path | None
    """Directory in which to cache OCR results."""

    language: Language
    """Scinoephile language."""

    retries: int
    """Google Lens OCR request attempts per uncached image."""


class _GoogleLensRequestError(RuntimeError):
    """Transient Google Lens request error returned as OCR text."""


class LensRecognizer:
    """Google Lens recognizer for image subtitles."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        language: Language = Language.eng,
        retries: int = 3,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            language: Scinoephile language
            retries: Google Lens OCR request attempts per uncached image
        """
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)
        try:
            self.language = language
            self.lens_language_code = _LENS_LANGUAGE_CODES[self.language]
        except (KeyError, ValueError) as exc:
            raise ValueError(f"{language} is not supported by Google Lens OCR") from exc
        self.retries = val_int(retries, min_value=1)
        self._lens_api_error_class = self._get_lens_api_error_class()
        self._api = self._get_lens_api_class()()

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"cache_dir_path={self.cache_dir_path!r}, "
            f"language={self.language!r}, "
            f"retries={self.retries!r})"
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
                lines = self._load_lens_lines(cache_path)
                cache_path.touch()
                logger.info(f"Loaded Google Lens OCR result from cache: {cache_path}")
                return self._format_lens_lines(lines)

            self._raise_if_running_loop()
            lines = self._recognize_image_uncached(image)
            self._save_lens_lines(lines, cache_path)
            logger.info(f"Saved Google Lens OCR result to cache: {cache_path}")
            return self._format_lens_lines(lines)

        self._raise_if_running_loop()
        lines = self._recognize_image_uncached(image)
        return self._format_lens_lines(lines)

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
            f"{image_sha256}_{image.mode}_{image.size}_{self.lens_language_code}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

    def _get_transient_error_classes(self) -> tuple[type[Exception], ...]:
        """Get exception classes that should trigger a Google Lens retry.

        Returns:
            transient exception classes
        """
        return self._lens_api_error_class, _GoogleLensRequestError

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
    def _get_lens_api_class() -> Any:
        """Import chrome-lens-py on demand.

        Returns:
            chrome-lens-py LensAPI class
        Raises:
            ImportError: if chrome-lens-py is not installed
        """
        try:
            from chrome_lens_py import (  # noqa: PLC0415
                LensAPI,
            )
        except ImportError as exc:
            raise ImportError(_OCR_EXTRA_MESSAGE) from exc
        return LensAPI

    @staticmethod
    def _get_lens_api_error_class() -> type[Exception]:
        """Import chrome-lens-py LensAPIError on demand.

        Returns:
            chrome-lens-py LensAPIError class
        Raises:
            ImportError: if chrome-lens-py is not installed
        """
        try:
            from chrome_lens_py.exceptions import (  # noqa: PLC0415
                LensAPIError,
            )
        except ImportError as module_exc:
            try:
                from chrome_lens_py import (  # noqa: PLC0415
                    LensAPIError,
                )
            except ImportError as package_exc:
                raise ImportError(_OCR_EXTRA_MESSAGE) from package_exc
            if module_exc.name != "chrome_lens_py.exceptions":
                logger.debug(
                    f"Imported LensAPIError from chrome_lens_py package after "
                    f"submodule import failed: {module_exc}"
                )
        return cast(type[Exception], LensAPIError)

    @staticmethod
    def _load_lens_lines(cache_path: Path) -> list[str]:
        """Load normalized Google Lens OCR lines from cache.

        Arguments:
            cache_path: cache file path
        Returns:
            normalized OCR lines
        """
        with cache_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            return []
        lines = data.get("lines")
        if not isinstance(lines, list):
            return []
        return [line for line in lines if isinstance(line, str)]

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
        transient_error_classes = self._get_transient_error_classes()

        async def recognize() -> list[str]:
            """Run Google Lens OCR retries in one event loop."""
            for attempt in range(1, self.retries + 1):
                try:
                    result = await self._api.process_image(
                        image_path=image,
                        ocr_language=self.lens_language_code,
                        ocr_preserve_line_breaks=True,
                        output_format="lines",
                    )
                    lines = self._normalize_lens_result(result)
                    self._raise_if_request_error(lines)
                except transient_error_classes as exc:
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

    @staticmethod
    def _save_lens_lines(lines: list[str], cache_path: Path):
        """Save normalized Google Lens OCR lines to cache.

        Arguments:
            lines: normalized Google Lens OCR lines
            cache_path: cache file path
        """
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        data = {"lines": lines}
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
