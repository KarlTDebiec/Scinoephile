#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR recognition engine."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, override

import numpy as np
from PIL import Image

from scinoephile.core import ScinoephileError

from .result import (
    PaddleOcrBoundingBox,
    PaddleOcrPoint,
    PaddleOcrTextResult,
    format_paddle_ocr_text,
)

__all__ = [
    "PaddleOcrRecognizer",
    "PaddleOcrRecognizerProtocol",
]


class PaddleOcrRecognizerProtocol(Protocol):
    """Protocol for PaddleOCR-compatible image recognizers."""

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """


class PaddleOcrRecognizer:
    """PaddleOCR recognizer for image subtitles."""

    def __init__(
        self,
        *,
        language: str = "en",
        min_confidence: float = 0.0,
    ):
        """Initialize.

        Arguments:
            language: PaddleOCR language code
            min_confidence: minimum confidence to include
        Raises:
            ScinoephileError: if PaddleOCR is unavailable
        """
        try:
            from paddleocr import PaddleOCR  # noqa: PLC0415
        except ImportError as exc:
            raise ScinoephileError(
                "PaddleOCR is not installed. Install Scinoephile with its PaddleOCR "
                "dependencies, or run `uv add paddleocr paddlepaddle`."
            ) from exc

        self.language = language
        self.min_confidence = min_confidence
        try:
            self._ocr = PaddleOCR(
                lang=language,
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=True,
            )
        except TypeError:
            self._ocr = PaddleOCR(lang=language)

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
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
        raw_results = self._predict(array)
        results = _normalize_paddle_ocr_results(raw_results)
        return format_paddle_ocr_text(results, min_confidence=self.min_confidence)

    def _predict(self, array: np.ndarray) -> Any:
        """Run PaddleOCR prediction.

        Arguments:
            array: RGB image array
        Returns:
            raw PaddleOCR results
        """
        predict = getattr(self._ocr, "predict", None)
        if isinstance(predict, Callable):
            return predict(array)
        ocr = getattr(self._ocr, "ocr")
        if isinstance(ocr, Callable):
            return ocr(array)
        raise ScinoephileError("PaddleOCR object does not expose a prediction method.")


def _normalize_paddle_ocr_results(raw_results: Any) -> list[PaddleOcrTextResult]:
    """Normalize raw PaddleOCR results.

    Arguments:
        raw_results: raw PaddleOCR output
    Returns:
        normalized text results
    """
    results: list[PaddleOcrTextResult] = []
    _collect_paddle_ocr_results(raw_results, results)
    return results


def _collect_paddle_ocr_results(
    value: Any,
    results: list[PaddleOcrTextResult],
):
    """Collect PaddleOCR text results recursively.

    Arguments:
        value: raw PaddleOCR value
        results: collected normalized results
    """
    if isinstance(value, dict):
        parsed = _parse_paddle_ocr_dict(value)
        if parsed is not None:
            results.append(parsed)
        for nested_value in value.values():
            _collect_paddle_ocr_results(nested_value, results)
        return

    if isinstance(value, list | tuple):
        parsed = _parse_paddle_ocr_sequence(value)
        if parsed is not None:
            results.append(parsed)
            return
        for nested_value in value:
            _collect_paddle_ocr_results(nested_value, results)


def _parse_paddle_ocr_dict(value: dict[Any, Any]) -> PaddleOcrTextResult | None:
    """Parse one PaddleOCR result dictionary.

    Arguments:
        value: raw result dictionary
    Returns:
        normalized result, if recognized
    """
    text = value.get("text") or value.get("rec_text")
    score = value.get("confidence") or value.get("score") or value.get("rec_score")
    points = value.get("points") or value.get("dt_polys") or value.get("bbox")
    if isinstance(text, str) and score is not None and points is not None:
        return _build_result(text, score, points)
    return None


def _parse_paddle_ocr_sequence(value: Any) -> PaddleOcrTextResult | None:
    """Parse one PaddleOCR result sequence.

    Arguments:
        value: raw result sequence
    Returns:
        normalized result, if recognized
    """
    if not isinstance(value, list | tuple) or len(value) < 2:
        return None

    points = value[0]
    text_and_score = value[1]
    if (
        isinstance(text_and_score, list | tuple)
        and len(text_and_score) >= 2
        and isinstance(text_and_score[0], str)
    ):
        return _build_result(text_and_score[0], text_and_score[1], points)
    return None


def _build_result(text: str, score: Any, points: Any) -> PaddleOcrTextResult | None:
    """Build a normalized PaddleOCR result.

    Arguments:
        text: recognized text
        score: recognition score
        points: raw bounding points
    Returns:
        normalized result, if raw data is valid
    """
    normalized_points = _normalize_points(points)
    if normalized_points is None:
        return None
    try:
        confidence = float(score)
    except (TypeError, ValueError):
        return None
    return PaddleOcrTextResult(
        text=text,
        confidence=confidence,
        bounding_box=PaddleOcrBoundingBox(
            top_left=normalized_points[0],
            top_right=normalized_points[1],
            bottom_right=normalized_points[2],
            bottom_left=normalized_points[3],
        ),
    )


def _normalize_points(points: Any) -> tuple[PaddleOcrPoint, ...] | None:
    """Normalize raw PaddleOCR points.

    Arguments:
        points: raw points
    Returns:
        four normalized points, if raw data is valid
    """
    try:
        normalized = tuple(
            PaddleOcrPoint(float(point[0]), float(point[1])) for point in points
        )
    except (TypeError, ValueError, IndexError):
        return None
    if len(normalized) != 4:
        return None
    return normalized
