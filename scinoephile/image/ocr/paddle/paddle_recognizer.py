#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR recognition engine."""

from __future__ import annotations

import os
from logging import getLogger
from pathlib import Path
from platform import system
from typing import Any, TypedDict, override

import numpy as np
from PIL import Image

from scinoephile.core import Language
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.dependencies.ocr import import_paddleocr

from .bounding_box import PaddleOcrBoundingBox
from .cache import PaddleCache
from .text_result import PaddleOcrTextResult

__all__ = ["PaddleRecognizer", "PaddleRecognizerKwargs"]

_TEXT_DETECTION_MODEL_NAME = "PP-OCRv5_server_det"
_TEXT_RECOGNITION_MODEL_NAME = "PP-OCRv5_server_rec"
_TEXTLINE_ORIENTATION_MODEL_NAME = "PP-LCNet_x1_0_textline_ori"
_PADDLE_LANGUAGE_CODES = {
    Language.eng: "en",
    Language.yue_hans: "ch",
    Language.yue_hant: "chinese_cht",
    Language.zho_hans: "ch",
    Language.zho_hant: "chinese_cht",
}


class PaddleRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to PaddleRecognizer."""

    cache_root_path: Path | None
    """Root directory beneath which to cache OCR results, or None for default."""

    language: Language
    """Scinoephile language."""

    min_confidence: float
    """Minimum confidence to include."""

    overwrite_cache: bool
    """Whether to replace matching OCR cache files."""


class PaddleRecognizer:
    """PaddleOCR recognizer for image subtitles."""

    def __init__(
        self,
        *,
        cache_root_path: Path | None = None,
        language: Language = Language.eng,
        min_confidence: float = 0.0,
        overwrite_cache: bool = False,
    ):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None for default
            language: Scinoephile language
            min_confidence: minimum confidence to include
            overwrite_cache: whether to replace matching OCR cache files
        Raises:
            ValueError: if language is unsupported
        """
        try:
            self.language = language
            self.paddle_language_code = _PADDLE_LANGUAGE_CODES[self.language]
        except (KeyError, ValueError) as exc:
            raise ValueError(f"{language} is not supported by PaddleOCR") from exc
        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

        self.min_confidence = min_confidence
        self._cache = PaddleCache(cache_root_path, overwrite_cache)
        self.runtime_identity = get_distribution_identity("paddleocr")
        """Installed PaddleOCR runtime identity."""

        paddleocr = import_paddleocr()
        root_logger = getLogger()
        root_logger_level = root_logger.level
        try:
            self._ocr = paddleocr.PaddleOCR(
                lang=self.paddle_language_code,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=True,
                text_detection_model_name=_TEXT_DETECTION_MODEL_NAME,
                text_recognition_model_name=_TEXT_RECOGNITION_MODEL_NAME,
                textline_orientation_model_name=_TEXTLINE_ORIENTATION_MODEL_NAME,
                enable_mkldnn=system() != "Windows",
            )
        finally:
            root_logger.setLevel(root_logger_level)

    @override
    def __repr__(self) -> str:
        """Get a reconstructable representation of this recognizer.

        Returns:
            constructor-like representation
        """
        return (
            f"{self.__class__.__name__}("
            f"cache_root_path={self._cache.cache_root_path!r}, "
            f"language={self.language!r}, "
            f"min_confidence={self.min_confidence!r}, "
            f"overwrite_cache={self._cache.overwrite!r})"
        )

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        array = np.array(image.convert("RGB"))
        cache_identity: CacheIdentity = {
            "language": self.paddle_language_code,
            "runtime": self.runtime_identity,
            "text_detection_model": _TEXT_DETECTION_MODEL_NAME,
            "text_recognition_model": _TEXT_RECOGNITION_MODEL_NAME,
            "textline_orientation_model": _TEXTLINE_ORIENTATION_MODEL_NAME,
        }
        if (results := self._cache.load(image, cache_identity)) is not None:
            return self._format_paddle_ocr_text(
                results, min_confidence=self.min_confidence
            )

        raw_results = self._ocr.predict(array)
        results = self._normalize_paddle_ocr_results(raw_results)
        self._cache.save(image, cache_identity, results)
        return self._format_paddle_ocr_text(results, min_confidence=self.min_confidence)

    @staticmethod
    def _format_paddle_ocr_text(
        results: list[PaddleOcrTextResult], *, min_confidence: float = 0.0
    ) -> str:
        """Format PaddleOCR results as subtitle text.

        Arguments:
            results: PaddleOCR text results
            min_confidence: minimum confidence to include
        Returns:
            subtitle text with ASS/SRT newline escapes
        """
        filtered_results = [
            result for result in results if result.confidence >= min_confidence
        ]
        if not filtered_results:
            return ""

        average_height = sum(
            result.bounding_box.height for result in filtered_results
        ) / len(filtered_results)
        sorted_results = sorted(
            filtered_results, key=lambda result: result.bounding_box.center[1]
        )
        lines: list[list[PaddleOcrTextResult]] = []
        line: list[PaddleOcrTextResult] = []
        previous_result: PaddleOcrTextResult | None = None

        for result in sorted_results:
            if previous_result is not None and (
                result.bounding_box.center[1]
                > previous_result.bounding_box.top_left[1] + average_height
            ):
                lines.append(
                    sorted(
                        line,
                        key=lambda line_result: line_result.bounding_box.top_left[0],
                    )
                )
                line = []
            line.append(result)
            previous_result = result

        if line:
            lines.append(
                sorted(
                    line, key=lambda line_result: line_result.bounding_box.top_left[0]
                )
            )

        return "\\N".join(" ".join(result.text for result in line) for line in lines)

    @staticmethod
    def _normalize_paddle_ocr_results(raw_results: Any) -> list[PaddleOcrTextResult]:
        """Normalize raw PaddleOCR results.

        Arguments:
            raw_results: raw PaddleOCR output
        Returns:
            normalized text results
        """
        results: list[PaddleOcrTextResult] = []
        if not isinstance(raw_results, list | tuple):
            return results

        for raw_result in raw_results:
            if not isinstance(raw_result, dict):
                continue
            texts = raw_result.get("rec_texts")
            scores = raw_result.get("rec_scores")
            polygons = raw_result.get("rec_polys")
            if polygons is None:
                polygons = raw_result.get("dt_polys")
            if not isinstance(texts, list | tuple):
                continue
            if not isinstance(scores, list | tuple):
                continue
            if not isinstance(polygons, list | tuple | np.ndarray):
                continue

            for text, score, polygon in zip(texts, scores, polygons, strict=False):
                if not isinstance(text, str):
                    continue
                try:
                    confidence = float(score)
                    normalized_points = tuple(
                        (float(point[0]), float(point[1])) for point in polygon
                    )
                except (TypeError, ValueError, IndexError):
                    continue
                if len(normalized_points) != 4:
                    continue
                results.append(
                    PaddleOcrTextResult(
                        text=text,
                        confidence=confidence,
                        bounding_box=PaddleOcrBoundingBox(
                            top_left=normalized_points[0],
                            top_right=normalized_points[1],
                            bottom_right=normalized_points[2],
                            bottom_left=normalized_points[3],
                        ),
                    )
                )
        return results
