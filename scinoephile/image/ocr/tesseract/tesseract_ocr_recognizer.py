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
from scinoephile.core import ScinoephileError

from .hocr import parse_tesseract_hocr, transfer_tesseract_hocr_italics
from .preprocessing import preprocess_tesseract_ocr_image

__all__ = [
    "TesseractOcrRecognizer",
]

logger = getLogger(__name__)


class TesseractOcrRecognizer:
    """Tesseract recognizer for image subtitles."""

    engine_version = "tesseract-4"
    """Tesseract cache version label."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        executable_path: Path | str = "tesseract",
        detect_italics: bool = False,
        language: str = "eng",
        legacy_tessdata_dir_path: Path | None = None,
        oem: int | None = 3,
        psm: int = 6,
        scale: int = 2,
        skip_executable_validation: bool = False,
        tessdata_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            executable_path: Tesseract executable path or command name
            detect_italics: whether to run a legacy-engine pass for italics
            language: Tesseract language code
            legacy_tessdata_dir_path: optional tessdata directory for legacy OCR
            oem: Tesseract OCR engine mode, or None to omit --oem
            psm: Tesseract page segmentation mode
            scale: image preprocessing scale
            skip_executable_validation: whether to skip executable validation
            tessdata_dir_path: optional tessdata directory
        """
        self.language = language
        self.detect_italics = detect_italics
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

        self.legacy_tessdata_dir_path: Path | None = None
        if legacy_tessdata_dir_path is not None:
            self.legacy_tessdata_dir_path = val_input_dir_path(legacy_tessdata_dir_path)

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"cache_dir_path={self.cache_dir_path!r}, "
            f"executable_path={self.executable_path!r}, "
            f"detect_italics={self.detect_italics!r}, "
            f"language={self.language!r}, "
            f"legacy_tessdata_dir_path={self.legacy_tessdata_dir_path!r}, "
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
            "hocr",
        ]
        if self.oem is not None:
            command[-1:-1] = ["--oem", str(self.oem)]
        if self.tessdata_dir_path is not None:
            command.extend(["--tessdata-dir", str(self.tessdata_dir_path)])
        return command

    def _build_legacy_italics_command(
        self,
        image_path: Path,
        output_base_path: Path,
    ) -> list[str]:
        """Build Tesseract legacy-engine hOCR command for italic detection.

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
            "0",
            "-c",
            "tessedit_create_hocr=1",
            "-c",
            "hocr_font_info=1",
        ]
        tessdata_dir_path = self.legacy_tessdata_dir_path or self.tessdata_dir_path
        if tessdata_dir_path is not None:
            command.extend(["--tessdata-dir", str(tessdata_dir_path)])
        return command

    def _build_legacy_fallback_command(
        self,
        image_path: Path,
        output_base_path: Path,
    ) -> list[str]:
        """Build Tesseract legacy-engine hOCR command for blank fallback.

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
            "7",
            "--oem",
            "0",
            "-c",
            "tessedit_create_hocr=1",
        ]
        tessdata_dir_path = self.legacy_tessdata_dir_path or self.tessdata_dir_path
        if tessdata_dir_path is not None:
            command.extend(["--tessdata-dir", str(tessdata_dir_path)])
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
            f"{self.executable_path}_{self.detect_italics}_{self.language}_"
            f"{self.legacy_tessdata_dir_path}_{self.oem}_{self.psm}_{self.scale}_"
            f"{self.tessdata_dir_path}"
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
        with TemporaryDirectory(prefix="scinoephile_tesseract_") as tmp_dir:
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
        with TemporaryDirectory(prefix="scinoephile_tesseract_") as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            image_path = tmp_dir_path / "input.png"
            output_base_path = tmp_dir_path / "output"
            preprocessed_image = preprocess_tesseract_ocr_image(
                image,
                scale=self.scale,
            )
            preprocessed_image.save(image_path)
            text = self._run_tesseract(image_path, output_base_path)
            if text.strip() or not self._uses_legacy_blank_fallback:
                return text

            fallback_image_path = tmp_dir_path / "input_legacy_fallback.png"
            fallback_output_base_path = tmp_dir_path / "output_legacy_fallback"
            fallback_image = preprocess_tesseract_ocr_image(image, scale=1)
            fallback_image.save(fallback_image_path)
            fallback_text = self._run_legacy_blank_fallback(
                fallback_image_path,
                fallback_output_base_path,
            )
            if self._is_usable_legacy_blank_fallback_text(fallback_text):
                logger.info(
                    "Using Tesseract legacy fallback for blank English OCR result"
                )
                return fallback_text
            return text

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
        hocr = self._read_hocr_output(output_base_path)
        if not self.detect_italics:
            return parse_tesseract_hocr(hocr)

        legacy_output_base_path = output_base_path.with_name(
            f"{output_base_path.name}_legacy_italics"
        )
        try:
            self._run_command(
                self._build_legacy_italics_command(
                    image_path,
                    legacy_output_base_path,
                )
            )
            legacy_hocr = self._read_hocr_output(legacy_output_base_path)
        except (OSError, ValueError) as exc:
            raise ScinoephileError(
                "Tesseract italic detection requires legacy Tesseract data. "
                "Install legacy-capable traineddata and pass "
                "--legacy-tessdata-dir if it is not in Tesseract's default "
                "tessdata directory."
            ) from exc

        return transfer_tesseract_hocr_italics(hocr, legacy_hocr)

    @property
    def _uses_legacy_blank_fallback(self) -> bool:
        """Whether to use legacy OCR as a blank-result fallback."""
        return (
            self.language == "eng"
            and (self.legacy_tessdata_dir_path is not None or self.tessdata_dir_path)
            is not None
        )

    def _run_legacy_blank_fallback(
        self,
        image_path: Path,
        output_base_path: Path,
    ) -> str:
        """Run Tesseract legacy-engine fallback and parse hOCR output.

        Arguments:
            image_path: input image path
            output_base_path: output base path without extension
        Returns:
            recognized text
        """
        try:
            self._run_command(
                self._build_legacy_fallback_command(image_path, output_base_path)
            )
            return parse_tesseract_hocr(self._read_hocr_output(output_base_path))
        except (OSError, ValueError) as exc:
            logger.info(f"Tesseract legacy blank fallback failed: {exc}")
            return ""

    @staticmethod
    def _is_usable_legacy_blank_fallback_text(text: str) -> bool:
        """Return whether legacy fallback text is useful enough to accept.

        Arguments:
            text: fallback text
        Returns:
            whether text should replace a blank primary OCR result
        """
        return any(char.isalpha() for char in text)

    @staticmethod
    def _read_hocr_output(output_base_path: Path) -> str:
        """Read Tesseract hOCR output.

        Arguments:
            output_base_path: output base path without extension
        Returns:
            hOCR HTML
        Raises:
            ValueError: if Tesseract produced no hOCR output file
        """
        for suffix in (".hocr", ".html"):
            hocr_path = output_base_path.with_suffix(suffix)
            if hocr_path.exists():
                return hocr_path.read_text(encoding="utf-8")
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
