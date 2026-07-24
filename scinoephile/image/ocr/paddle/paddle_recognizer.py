#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR recognition engine."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict
from logging import getLogger
from pathlib import Path
from platform import system
from typing import Any, TypedDict, override

import numpy as np
from PIL import Image

from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import Language

from .bounding_box import PaddleOcrBoundingBox
from .text_result import PaddleOcrTextResult

__all__ = [
    "PaddleRecognizer",
    "PaddleRecognizerKwargs",
]

logger = getLogger(__name__)

_TEXT_DETECTION_MODEL_NAME = "PP-OCRv5_server_det"
_TEXT_RECOGNITION_MODEL_NAME = "PP-OCRv5_server_rec"
_TEXTLINE_ORIENTATION_MODEL_NAME = "PP-LCNet_x1_0_textline_ori"
_OCR_EXTRA_MESSAGE = (
    "PaddleOCR support requires optional OCR dependencies. "
    "Install scinoephile with the 'ocr' extra."
)
_PADDLE_LANGUAGE_CODES = {
    Language.eng: "en",
    Language.yue_hans: "ch",
    Language.yue_hant: "chinese_cht",
    Language.zho_hans: "ch",
    Language.zho_hant: "chinese_cht",
}


class PaddleRecognizerKwargs(TypedDict, total=False):
    """Additional keyword arguments forwarded to PaddleRecognizer."""

    cache_dir_path: Path | None
    """Directory in which to cache OCR results."""

    language: Language
    """Scinoephile language."""

    min_confidence: float
    """Minimum confidence to include."""


class PaddleRecognizer:
    """PaddleOCR recognizer for image subtitles."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        language: Language = Language.eng,
        min_confidence: float = 0.0,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            language: Scinoephile language
            min_confidence: minimum confidence to include
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
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

        paddle_ocr_cls = self._import_paddleocr_paddle_ocr()
        root_logger = getLogger()
        root_logger_level = root_logger.level
        try:
            self._ocr = paddle_ocr_cls(
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
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"cache_dir_path={self.cache_dir_path!r}, "
            f"language={self.language!r}, "
            f"min_confidence={self.min_confidence!r})"
        )

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        array = np.array(image.convert("RGB"))
        if (cache_path := self._get_cache_path(image)) is not None:
            if cache_path.exists():
                results = self._load_paddle_ocr_results(cache_path)
                cache_path.touch()
                logger.info(f"Loaded PaddleOCR result from cache: {cache_path}")
                return self._format_paddle_ocr_text(
                    results, min_confidence=self.min_confidence
                )

            raw_results = self._ocr.predict(array)
            results = self._normalize_paddle_ocr_results(raw_results)
            self._save_paddle_ocr_results(results, cache_path)
            logger.info(f"Saved PaddleOCR result to cache: {cache_path}")
            return self._format_paddle_ocr_text(
                results, min_confidence=self.min_confidence
            )

        raw_results = self._ocr.predict(array)
        results = self._normalize_paddle_ocr_results(raw_results)
        return self._format_paddle_ocr_text(results, min_confidence=self.min_confidence)

    def _get_cache_path(self, image: Image.Image) -> Path | None:
        """Get cache path based on hash of image data and OCR configuration.

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
            f"{image_sha256}_{image.mode}_{image.size}_{self.paddle_language_code}_"
            f"{_TEXT_DETECTION_MODEL_NAME}_"
            f"{_TEXT_RECOGNITION_MODEL_NAME}_"
            f"{_TEXTLINE_ORIENTATION_MODEL_NAME}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

    @staticmethod
    def _import_paddleocr_paddle_ocr() -> Any:
        """Import PaddleOCR on demand."""
        try:
            from paddleocr import (  # noqa: PLC0415
                PaddleOCR,
            )
        except ImportError as exc:
            raise ImportError(_OCR_EXTRA_MESSAGE) from exc
        return PaddleOCR

    @staticmethod
    def _format_paddle_ocr_text(
        results: list[PaddleOcrTextResult],
        *,
        min_confidence: float = 0.0,
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
            filtered_results,
            key=lambda result: result.bounding_box.center[1],
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
                    line,
                    key=lambda line_result: line_result.bounding_box.top_left[0],
                )
            )

        return "\\N".join(" ".join(result.text for result in line) for line in lines)

    @staticmethod
    def _load_paddle_ocr_results(cache_path: Path) -> list[PaddleOcrTextResult]:
        """Load normalized PaddleOCR results from cache.

        Arguments:
            cache_path: cache file path
        Returns:
            normalized PaddleOCR results
        """
        with cache_path.open("r", encoding="utf-8") as file:
            raw_results = json.load(file)
        results = []
        for result in raw_results:
            bounding_box = result["bounding_box"]
            points = {}
            for key in ("top_left", "top_right", "bottom_right", "bottom_left"):
                point = bounding_box[key]
                if isinstance(point, dict):
                    points[key] = (float(point["x"]), float(point["y"]))
                else:
                    points[key] = (float(point[0]), float(point[1]))
            results.append(
                PaddleOcrTextResult(
                    text=result["text"],
                    confidence=float(result["confidence"]),
                    bounding_box=PaddleOcrBoundingBox(
                        top_left=points["top_left"],
                        top_right=points["top_right"],
                        bottom_right=points["bottom_right"],
                        bottom_left=points["bottom_left"],
                    ),
                )
            )
        return results

    @staticmethod
    def _normalize_paddle_ocr_results(
        raw_results: Any,
    ) -> list[PaddleOcrTextResult]:
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

    @staticmethod
    def _save_paddle_ocr_results(
        results: list[PaddleOcrTextResult],
        cache_path: Path,
    ):
        """Save normalized PaddleOCR results to cache.

        Arguments:
            results: normalized PaddleOCR results
            cache_path: cache file path
        """
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with cache_path.open("w", encoding="utf-8") as file:
            json.dump([asdict(result) for result in results], file, ensure_ascii=False)
