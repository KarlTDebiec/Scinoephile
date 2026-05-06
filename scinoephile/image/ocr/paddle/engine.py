#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""PaddleOCR recognition engine."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable
from dataclasses import asdict
from logging import getLogger
from pathlib import Path
from typing import Any, Protocol, override

import numpy as np
from PIL import Image

from scinoephile.common.validation import val_output_dir_path
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

logger = getLogger(__name__)

_SUBTITLEEDIT_MODEL_ROOT_PATH = (
    Path.home()
    / "Library"
    / "Application Support"
    / "Subtitle Edit"
    / "OCR"
    / "PaddleOCR3-1"
    / "models"
)

_ARABIC_LANGUAGE_CODES = {"ar", "fa", "ug", "ur"}
_CYRILLIC_LANGUAGE_CODES = {
    "rs_cyrillic",
    "bg",
    "mn",
    "abq",
    "ady",
    "kbd",
    "ava",
    "dar",
    "inh",
    "che",
    "lbe",
    "lez",
    "tab",
}
_DEVANAGARI_LANGUAGE_CODES = {
    "hi",
    "mr",
    "ne",
    "bh",
    "mai",
    "ang",
    "bho",
    "mah",
    "sck",
    "new",
    "gom",
    "bgc",
    "sa",
}
_ESLAV_LANGUAGE_CODES = {"ru", "be", "uk"}
_LATIN_LANGUAGE_CODES = {
    "af",
    "az",
    "bs",
    "cs",
    "cy",
    "da",
    "de",
    "es",
    "et",
    "fr",
    "ga",
    "hr",
    "hu",
    "id",
    "is",
    "it",
    "ku",
    "la",
    "lt",
    "lv",
    "mi",
    "ms",
    "mt",
    "nl",
    "no",
    "oc",
    "pi",
    "pl",
    "pt",
    "ro",
    "rs_latin",
    "sk",
    "sl",
    "sq",
    "sv",
    "sw",
    "tl",
    "tr",
    "uz",
    "vi",
    "french",
    "german",
}


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
        cache_dir_path: Path | None = None,
        language: str = "en",
        min_confidence: float = 0.0,
        model_root_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            language: PaddleOCR language code
            min_confidence: minimum confidence to include
            model_root_dir_path: optional root containing SubtitleEdit PaddleOCR models
        Raises:
            ScinoephileError: if PaddleOCR is unavailable
        """
        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
        try:
            from paddleocr import PaddleOCR  # noqa: PLC0415
        except ImportError as exc:
            raise ScinoephileError(
                "PaddleOCR is not installed. Install Scinoephile with its PaddleOCR "
                "dependencies, or run `uv add paddleocr paddlepaddle`."
            ) from exc

        self.language = language
        self.min_confidence = min_confidence
        self.model_root_dir_path = model_root_dir_path
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)
        self.text_detection_model_name = _get_text_detection_model_name(language)
        self.text_recognition_model_name = _get_text_recognition_model_name(language)
        self.textline_orientation_model_name = "PP-LCNet_x1_0_textline_ori"

        kwargs = {
            "lang": language,
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": True,
            "text_detection_model_name": self.text_detection_model_name,
            "text_recognition_model_name": self.text_recognition_model_name,
            "textline_orientation_model_name": self.textline_orientation_model_name,
        }
        model_root_dir_path = model_root_dir_path or _get_subtitleedit_model_root()
        if model_root_dir_path is not None:
            kwargs.update(
                _get_model_dir_kwargs(
                    model_root_dir_path,
                    text_detection_model_name=self.text_detection_model_name,
                    text_recognition_model_name=self.text_recognition_model_name,
                    textline_orientation_model_name=self.textline_orientation_model_name,
                )
            )

        self._ocr = PaddleOCR(**kwargs)

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"{self.__class__.__name__}("
            f"cache_dir_path={self.cache_dir_path!r}, "
            f"language={self.language!r}, "
            f"min_confidence={self.min_confidence!r}, "
            f"model_root_dir_path={self.model_root_dir_path!r})"
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
                results = _load_paddle_ocr_results(cache_path)
                cache_path.touch()
                logger.info(f"Loaded PaddleOCR result from cache: {cache_path}")
                return format_paddle_ocr_text(
                    results, min_confidence=self.min_confidence
                )

            raw_results = self._predict(array)
            results = _normalize_paddle_ocr_results(raw_results)
            _save_paddle_ocr_results(results, cache_path)
            logger.info(f"Saved PaddleOCR result to cache: {cache_path}")
            return format_paddle_ocr_text(results, min_confidence=self.min_confidence)

        raw_results = self._predict(array)
        results = _normalize_paddle_ocr_results(raw_results)
        return format_paddle_ocr_text(results, min_confidence=self.min_confidence)

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
            f"{image_sha256}_{image.mode}_{image.size}_{self.language}_"
            f"{getattr(self, 'text_detection_model_name', '')}_"
            f"{getattr(self, 'text_recognition_model_name', '')}_"
            f"{getattr(self, 'textline_orientation_model_name', '')}"
        )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"

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


def _load_paddle_ocr_results(cache_path: Path) -> list[PaddleOcrTextResult]:
    """Load normalized PaddleOCR results from cache.

    Arguments:
        cache_path: cache file path
    Returns:
        normalized PaddleOCR results
    """
    with cache_path.open("r", encoding="utf-8") as file:
        raw_results = json.load(file)
    return [_parse_cached_paddle_ocr_result(result) for result in raw_results]


def _get_model_dir_kwargs(
    model_root_dir_path: Path,
    *,
    text_detection_model_name: str,
    text_recognition_model_name: str,
    textline_orientation_model_name: str,
) -> dict[str, str]:
    """Get PaddleOCR model directory keyword arguments.

    Arguments:
        model_root_dir_path: root directory containing SubtitleEdit PaddleOCR models
        text_detection_model_name: text detection model name
        text_recognition_model_name: text recognition model name
        textline_orientation_model_name: textline orientation model name
    Returns:
        keyword arguments for model directories that exist locally
    """
    candidates = {
        "text_detection_model_dir": (
            model_root_dir_path / "det",
            text_detection_model_name,
        ),
        "text_recognition_model_dir": (
            model_root_dir_path / "rec",
            text_recognition_model_name,
        ),
        "textline_orientation_model_dir": (
            model_root_dir_path / "cls",
            textline_orientation_model_name,
        ),
    }
    kwargs = {}
    for key, (parent_dir_path, model_name) in candidates.items():
        model_dir_path = _find_model_dir_path(parent_dir_path, model_name)
        if model_dir_path is not None:
            kwargs[key] = str(model_dir_path)
    return kwargs


def _get_subtitleedit_model_root() -> Path | None:
    """Get SubtitleEdit's local PaddleOCR model root path, if present.

    Returns:
        SubtitleEdit model root path, if available
    """
    model_root_dir_path = Path(
        os.environ.get(
            "SCINOEPHILE_PADDLEOCR_MODEL_ROOT",
            str(_SUBTITLEEDIT_MODEL_ROOT_PATH),
        )
    )
    if model_root_dir_path.exists():
        return model_root_dir_path
    return None


def _get_text_detection_model_name(language: str) -> str:
    """Get SubtitleEdit-compatible PaddleOCR text detection model name.

    Arguments:
        language: PaddleOCR language code
    Returns:
        text detection model name
    """
    if language in {
        "ch",
        "chinese_cht",
        "en",
        "japan",
        "korean",
        *_ESLAV_LANGUAGE_CODES,
        *_LATIN_LANGUAGE_CODES,
    }:
        return "PP-OCRv5_server_det"
    return "PP-OCRv3_mobile_det"


def _get_text_recognition_model_name(language: str) -> str:
    """Get SubtitleEdit-compatible PaddleOCR text recognition model name.

    Arguments:
        language: PaddleOCR language code
    Returns:
        text recognition model name
    """
    model_name = "latin_PP-OCRv5_mobile_rec"
    if language in {"ch", "chinese_cht", "en", "japan"}:
        model_name = "PP-OCRv5_server_rec"
    elif language in _ARABIC_LANGUAGE_CODES:
        model_name = "arabic_PP-OCRv3_mobile_rec"
    elif language in _ESLAV_LANGUAGE_CODES:
        model_name = "eslav_PP-OCRv5_mobile_rec"
    elif language in _CYRILLIC_LANGUAGE_CODES:
        model_name = "cyrillic_PP-OCRv3_mobile_rec"
    elif language in _DEVANAGARI_LANGUAGE_CODES:
        model_name = "devanagari_PP-OCRv3_mobile_rec"
    elif language == "korean":
        model_name = "korean_PP-OCRv5_mobile_rec"
    return model_name


def _find_model_dir_path(parent_dir_path: Path, model_name: str) -> Path | None:
    """Find a model directory under SubtitleEdit's support-file layout.

    Arguments:
        parent_dir_path: parent directory for one model type
        model_name: model name to find
    Returns:
        directory containing model files, if present
    """
    direct_model_dir_path = parent_dir_path / model_name
    for model_dir_path in [direct_model_dir_path, *direct_model_dir_path.glob("**/*")]:
        if not model_dir_path.is_dir() or model_dir_path.name != model_name:
            continue
        if any(
            (model_dir_path / file_name).exists()
            for file_name in ("inference.json", "inference.pdmodel", "config.json")
        ):
            return model_dir_path
    return None


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


def _parse_cached_paddle_ocr_result(value: dict[str, Any]) -> PaddleOcrTextResult:
    """Parse one normalized PaddleOCR result from cache.

    Arguments:
        value: cached result dictionary
    Returns:
        normalized PaddleOCR result
    """
    bounding_box = value["bounding_box"]
    return PaddleOcrTextResult(
        text=value["text"],
        confidence=float(value["confidence"]),
        bounding_box=PaddleOcrBoundingBox(
            top_left=_parse_cached_paddle_ocr_point(bounding_box["top_left"]),
            top_right=_parse_cached_paddle_ocr_point(bounding_box["top_right"]),
            bottom_right=_parse_cached_paddle_ocr_point(bounding_box["bottom_right"]),
            bottom_left=_parse_cached_paddle_ocr_point(bounding_box["bottom_left"]),
        ),
    )


def _parse_cached_paddle_ocr_point(value: dict[str, Any]) -> PaddleOcrPoint:
    """Parse one normalized PaddleOCR point from cache.

    Arguments:
        value: cached point dictionary
    Returns:
        normalized PaddleOCR point
    """
    return PaddleOcrPoint(float(value["x"]), float(value["y"]))


def _save_paddle_ocr_results(results: list[PaddleOcrTextResult], cache_path: Path):
    """Save normalized PaddleOCR results to cache.

    Arguments:
        results: normalized PaddleOCR results
        cache_path: cache file path
    """
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with cache_path.open("w", encoding="utf-8") as file:
        json.dump([asdict(result) for result in results], file, ensure_ascii=False)


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
        parsed_results = _parse_paddle_ocr_result_dict(value)
        if parsed_results:
            results.extend(parsed_results)
            return
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


def _parse_paddle_ocr_result_dict(
    value: dict[Any, Any],
) -> list[PaddleOcrTextResult]:
    """Parse a PaddleOCR 3 result dictionary.

    Arguments:
        value: raw PaddleOCR result dictionary
    Returns:
        normalized text results
    """
    texts = value.get("rec_texts")
    scores = value.get("rec_scores")
    polygons = value.get("rec_polys")
    if polygons is None:
        polygons = value.get("dt_polys")
    if not isinstance(texts, list | tuple):
        return []
    if not isinstance(scores, list | tuple):
        return []
    if not isinstance(polygons, list | tuple | np.ndarray):
        return []

    results = []
    for text, score, polygon in zip(texts, scores, polygons, strict=False):
        if not isinstance(text, str):
            continue
        result = _build_result(text, score, polygon)
        if result is not None:
            results.append(result)
    return results


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
