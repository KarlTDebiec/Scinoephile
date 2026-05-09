#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract OCR recognition engines."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

from PIL import Image

from scinoephile.common.subprocess import run_command
from scinoephile.common.validation import (
    val_executable,
    val_input_dir_path,
    val_output_dir_path,
)

from .hocr import parse_tesseract_hocr
from .preprocessing import preprocess_tesseract_ocr_image

__all__ = [
    "Tesseract4OcrRecognizer",
    "Tesseract5OcrRecognizer",
    "TesseractOcrRecognizer",
]

logger = getLogger(__name__)


class TesseractOcrRecognizer:
    """Base Tesseract recognizer for image subtitles."""

    engine_version = ""
    """Tesseract major version label used for cache namespacing."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        executable_path: Path | str = "tesseract",
        language: str = "eng",
        oem: int = 3,
        psm: int = 6,
        scale: int = 2,
        skip_executable_validation: bool = False,
        tessdata_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            executable_path: Tesseract executable path or command name
            language: Tesseract language code
            oem: Tesseract OCR engine mode
            psm: Tesseract page segmentation mode
            scale: image preprocessing scale
            skip_executable_validation: whether to skip executable validation
            tessdata_dir_path: optional tessdata directory
        """
        self.language = language
        self.oem = oem
        self.psm = psm
        self.scale = scale

        self.cache_dir_path: Path | None = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

        if skip_executable_validation:
            self.executable_path = Path(executable_path)
        else:
            self.executable_path = val_executable(str(executable_path))

        self.tessdata_dir_path: Path | None = None
        if tessdata_dir_path is not None:
            self.tessdata_dir_path = val_input_dir_path(tessdata_dir_path)

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"cache_dir_path={self.cache_dir_path!r}, "
            f"executable_path={self.executable_path!r}, "
            f"language={self.language!r}, "
            f"oem={self.oem!r}, "
            f"psm={self.psm!r}, "
            f"scale={self.scale!r}, "
            f"tessdata_dir_path={self.tessdata_dir_path!r})"
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
                text = self._load_result(cache_path)
                cache_path.touch()
                logger.info(f"Loaded Tesseract OCR result from cache: {cache_path}")
                return text

            text = self._recognize_uncached_image(image)
            self._save_result(text, cache_path)
            logger.info(f"Saved Tesseract OCR result to cache: {cache_path}")
            return text

        return self._recognize_uncached_image(image)

    def _build_command(self, image_path: Path, output_base_path: Path) -> list[str]:
        """Build Tesseract hOCR command.

        Arguments:
            image_path: input image path
            output_base_path: output base path without extension
        Returns:
            command arguments
        """
        command = [
            str(self.executable_path),
            str(image_path),
            str(output_base_path),
            "-l",
            self.language,
            "--psm",
            str(self.psm),
            "--oem",
            str(self.oem),
            "hocr",
        ]
        if self.tessdata_dir_path is not None:
            command.extend(["--tessdata-dir", str(self.tessdata_dir_path)])
        return command

    def _get_cache_path(self, image: Image.Image) -> Path | None:
        """Get cache path based on image data and OCR configuration.

        Arguments:
            image: image used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None

        image_sha256 = hashlib.sha256(image.tobytes()).hexdigest()
        cache_key = (
            f"{image_sha256}_{image.mode}_{image.size}_{self.engine_version}_"
            f"{self.executable_path}_{self.language}_{self.oem}_{self.psm}_"
            f"{self.scale}_{self.tessdata_dir_path}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

    @staticmethod
    def _load_result(cache_path: Path) -> str:
        """Load recognized text from cache.

        Arguments:
            cache_path: cache file path
        Returns:
            recognized text
        """
        with cache_path.open("r", encoding="utf-8") as file:
            result = json.load(file)
        return str(result["text"])

    def _recognize_preprocessed_image(self, image: Image.Image) -> str:
        """Recognize text from a preprocessed image.

        Arguments:
            image: preprocessed image
        Returns:
            recognized text
        """
        with TemporaryDirectory(
            prefix=f"scinoephile_tesseract{self.engine_version}_"
        ) as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            image_path = tmp_dir_path / "input.png"
            output_base_path = tmp_dir_path / "output"
            image.save(image_path)
            return self._run_tesseract(image_path, output_base_path)

    def _recognize_uncached_image(self, image: Image.Image) -> str:
        """Preprocess and recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        preprocessed_image = preprocess_tesseract_ocr_image(image, scale=self.scale)
        return self._recognize_preprocessed_image(preprocessed_image)

    def _run_command(self, command: list[str]) -> tuple[int, str, str]:
        """Run command.

        Arguments:
            command: command arguments
        Returns:
            exit code, stdout, and stderr
        """
        return run_command(command)

    def _run_tesseract(self, image_path: Path, output_base_path: Path) -> str:
        """Run Tesseract and parse hOCR output.

        Arguments:
            image_path: input image path
            output_base_path: output base path without extension
        Returns:
            recognized text
        """
        self._run_command(self._build_command(image_path, output_base_path))
        for suffix in (".hocr", ".html"):
            hocr_path = output_base_path.with_suffix(suffix)
            if hocr_path.exists():
                return parse_tesseract_hocr(hocr_path.read_text(encoding="utf-8"))
        raise ValueError(
            "Tesseract command completed but did not produce hOCR output "
            f"at {output_base_path.with_suffix('.hocr')} or "
            f"{output_base_path.with_suffix('.html')}"
        )

    @staticmethod
    def _save_result(text: str, cache_path: Path):
        """Save recognized text to cache.

        Arguments:
            text: recognized text
            cache_path: cache file path
        """
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump({"text": text}, file, ensure_ascii=False)


class Tesseract4OcrRecognizer(TesseractOcrRecognizer):
    """Tesseract 4 recognizer for image subtitles."""

    engine_version = "4"
    """Tesseract major version label used for cache namespacing."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        executable_path: Path | str = "tesseract",
        language: str = "eng",
        oem: int = 1,
        psm: int = 6,
        scale: int = 2,
        skip_executable_validation: bool = False,
        tessdata_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            executable_path: Tesseract executable path or command name
            language: Tesseract language code
            oem: Tesseract OCR engine mode
            psm: Tesseract page segmentation mode
            scale: image preprocessing scale
            skip_executable_validation: whether to skip executable validation
            tessdata_dir_path: optional tessdata directory
        """
        super().__init__(
            cache_dir_path=cache_dir_path,
            executable_path=executable_path,
            language=language,
            oem=oem,
            psm=psm,
            scale=scale,
            skip_executable_validation=skip_executable_validation,
            tessdata_dir_path=tessdata_dir_path,
        )


class Tesseract5OcrRecognizer(TesseractOcrRecognizer):
    """Tesseract 5 recognizer for image subtitles."""

    engine_version = "5"
    """Tesseract major version label used for cache namespacing."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        executable_path: Path | str = "tesseract",
        language: str = "eng",
        oem: int = 3,
        psm: int = 6,
        scale: int = 2,
        skip_executable_validation: bool = False,
        tessdata_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            executable_path: Tesseract executable path or command name
            language: Tesseract language code
            oem: Tesseract OCR engine mode
            psm: Tesseract page segmentation mode
            scale: image preprocessing scale
            skip_executable_validation: whether to skip executable validation
            tessdata_dir_path: optional tessdata directory
        """
        super().__init__(
            cache_dir_path=cache_dir_path,
            executable_path=executable_path,
            language=language,
            oem=oem,
            psm=psm,
            scale=scale,
            skip_executable_validation=skip_executable_validation,
            tessdata_dir_path=tessdata_dir_path,
        )
