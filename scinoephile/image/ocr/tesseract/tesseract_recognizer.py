#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tesseract OCR recognition engines."""

from __future__ import annotations

import hashlib
import json
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TypedDict, override

import requests
from PIL import Image

from scinoephile.common.subprocess import run_command
from scinoephile.common.validation import (
    val_executable,
    val_input_dir_path,
    val_output_dir_path,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path

from .hocr import parse_tesseract_hocr, transfer_tesseract_hocr_italics
from .preprocessing import preprocess_tesseract_ocr_image

__all__ = [
    "TesseractRecognizer",
    "TesseractRecognizerKwargs",
]

logger = getLogger(__name__)

TESSERACT_LEGACY_TESSDATA_URL_TEMPLATE = (
    "https://raw.githubusercontent.com/tesseract-ocr/tessdata/master/"
    "{language}.traineddata"
)
"""URL template for legacy-capable Tesseract traineddata."""
_TESSERACT_LANGUAGE_CODES = {
    Language.eng: "eng",
    Language.yue_hans: "chi_sim",
    Language.yue_hant: "chi_tra",
    Language.zho_hans: "chi_sim",
    Language.zho_hant: "chi_tra",
}


class TesseractRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to TesseractRecognizer."""

    cache_dir_path: Path | None
    """Directory in which to cache OCR results."""

    detect_italics: bool
    """Whether to run a legacy-engine pass for italics."""

    executable_path: Path | str
    """Tesseract executable path or command name."""

    language: Language
    """Scinoephile language."""

    oem: int | None
    """Tesseract OCR engine mode, or None to omit --oem."""

    psm: int
    """Tesseract page segmentation mode."""

    scale: int
    """Image preprocessing scale."""

    skip_executable_validation: bool
    """Whether to skip executable validation."""

    tessdata_dir_path: Path | None
    """Optional tessdata directory."""


class TesseractRecognizer:
    """Tesseract recognizer for image subtitles."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        executable_path: Path | str = "tesseract",
        detect_italics: bool = False,
        language: Language = Language.eng,
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
            language: Scinoephile language
            oem: Tesseract OCR engine mode, or None to omit --oem
            psm: Tesseract page segmentation mode
            scale: image preprocessing scale
            skip_executable_validation: whether to skip executable validation
            tessdata_dir_path: optional tessdata directory
        """
        self.language = language
        if detect_italics and self.language is not Language.eng:
            raise ValueError(
                "Tesseract italic detection is only supported with language eng"
            )
        try:
            self.tesseract_language_code = _TESSERACT_LANGUAGE_CODES[self.language]
        except KeyError as exc:
            raise ValueError(
                f"{self.language} is not supported by Tesseract OCR"
            ) from exc

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

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"cache_dir_path={self.cache_dir_path!r}, "
            f"executable_path={self.executable_path!r}, "
            f"detect_italics={self.detect_italics!r}, "
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

    @property
    def _hocr_word_separator(self) -> str:
        """Text with which to join hOCR word spans."""
        if self.tesseract_language_code.startswith("chi_"):
            return ""
        return " "

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
            self.tesseract_language_code,
            "--psm",
            str(self.psm),
            "hocr",
        ]
        if self.oem is not None:
            command[-1:-1] = ["--oem", str(self.oem)]
        if self.tessdata_dir_path is not None:
            command[-1:-1] = ["--tessdata-dir", str(self.tessdata_dir_path)]
        return command

    def _build_legacy_command(
        self,
        image_path: Path,
        output_base_path: Path,
        *,
        psm: int,
        include_font_info: bool = False,
    ) -> list[str]:
        """Build a Tesseract legacy-engine hOCR command.

        Arguments:
            image_path: input image path
            output_base_path: output base path without extension
            psm: Tesseract page segmentation mode
            include_font_info: whether to request hOCR font metadata
        Returns:
            command arguments
        """
        command = [
            str(self.executable_path),
            str(image_path),
            str(output_base_path),
            "-l",
            self.tesseract_language_code,
            "--psm",
            str(psm),
            "--oem",
            "0",
            "-c",
            "tessedit_create_hocr=1",
        ]
        if include_font_info:
            command.extend(["-c", "hocr_font_info=1"])
        command.extend(["--tessdata-dir", str(self._get_legacy_tessdata_dir_path())])
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
        return self._build_legacy_command(image_path, output_base_path, psm=7)

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
        return self._build_legacy_command(
            image_path,
            output_base_path,
            psm=self.psm,
            include_font_info=True,
        )

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
            f"{image_sha256}_{image.mode}_{image.size}_{self.executable_path}_"
            f"{self.detect_italics}_{self.tesseract_language_code}_{self.oem}_"
            f"{self.psm}_"
            f"{self.scale}_{self.tessdata_dir_path}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

    def _download_legacy_traineddata(self, traineddata_path: Path):
        """Download legacy-capable Tesseract traineddata.

        Arguments:
            traineddata_path: destination traineddata path
        Raises:
            ScinoephileError: if the download fails
        """
        url = TESSERACT_LEGACY_TESSDATA_URL_TEMPLATE.format(
            language=self.tesseract_language_code
        )
        temp_traineddata_path = traineddata_path.with_suffix(".traineddata.tmp")
        logger.info(f"Downloading Tesseract legacy traineddata: {url}")
        try:
            response = requests.get(url, timeout=60.0)
            response.raise_for_status()
            temp_traineddata_path.write_bytes(response.content)
            temp_traineddata_path.replace(traineddata_path)
        except (OSError, requests.RequestException) as exc:
            temp_traineddata_path.unlink(missing_ok=True)
            raise ScinoephileError(
                "Tesseract legacy OCR requires legacy-capable traineddata. "
                "Failed to download "
                f"{self.tesseract_language_code}.traineddata from {url}."
            ) from exc
        logger.info(f"Downloaded Tesseract legacy traineddata: {traineddata_path}")

    def _get_legacy_tessdata_dir_path(self) -> Path:
        """Get legacy-capable Tesseract tessdata directory path.

        Returns:
            legacy tessdata directory path
        """
        if self.cache_dir_path is None:
            legacy_tessdata_dir_path = get_runtime_cache_dir_path(
                "tesseract", "legacy-tessdata"
            )
        else:
            legacy_tessdata_dir_path = val_output_dir_path(
                self.cache_dir_path / "legacy-tessdata"
            )

        traineddata_path = (
            legacy_tessdata_dir_path / f"{self.tesseract_language_code}.traineddata"
        )
        if not traineddata_path.exists():
            self._download_legacy_traineddata(traineddata_path)
        return legacy_tessdata_dir_path

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
            preprocessed_image = preprocess_tesseract_ocr_image(image, scale=self.scale)
            preprocessed_image.save(image_path)
            text = self._run_tesseract(image_path, output_base_path)
            if text.strip():
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
                    "Using Tesseract legacy fallback for blank OCR result "
                    f"with language {self.tesseract_language_code}"
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
            return parse_tesseract_hocr(
                self._read_hocr_output(output_base_path),
                word_separator=self._hocr_word_separator,
            )
        except (OSError, ScinoephileError, ValueError) as exc:
            logger.info(f"Tesseract legacy blank fallback failed: {exc}")
            return ""

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
            return parse_tesseract_hocr(hocr, word_separator=self._hocr_word_separator)

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
                "Scinoephile downloads legacy-capable traineddata to its "
                "Tesseract cache directory when needed."
            ) from exc

        return transfer_tesseract_hocr_italics(hocr, legacy_hocr)

    @staticmethod
    def _is_usable_legacy_blank_fallback_text(text: str) -> bool:
        """Return whether legacy fallback text is useful enough to accept.

        Arguments:
            text: fallback text
        Returns:
            whether text should replace a blank primary OCR result
        """
        return any(char.isalpha() or "\u4e00" <= char <= "\u9fff" for char in text)

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
