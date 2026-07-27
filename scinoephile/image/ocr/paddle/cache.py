#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Caches PaddleOCR results."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict
from pathlib import Path
from typing import cast

from scinoephile.image.ocr.cache import OcrCache

from .bounding_box import PaddleOcrBoundingBox
from .text_result import PaddleOcrTextResult

__all__ = ["PaddleOcrCache"]


class PaddleOcrCache(OcrCache[list[PaddleOcrTextResult]]):
    """Caches normalized PaddleOCR text results."""

    def __init__(self, cache_root_path: Path | None, overwrite: bool = False):
        """Initialize.

        Arguments:
            cache_root_path: root directory beneath which to cache, or None to disable
            overwrite: whether to replace matching cache files
        """
        super().__init__(cache_root_path, "paddleocr", "PaddleOCR", overwrite)

    def _deserialize(self, payload: object) -> list[PaddleOcrTextResult]:
        """Deserialize and validate normalized PaddleOCR results.

        Arguments:
            payload: decoded JSON payload
        Returns:
            normalized PaddleOCR results
        """
        if not isinstance(payload, list):
            raise ValueError("PaddleOCR cache must contain a list")

        results: list[PaddleOcrTextResult] = []
        for raw_result in payload:
            if not isinstance(raw_result, Mapping):
                raise ValueError("PaddleOCR cache entries must be objects")
            raw_result = cast(Mapping[str, object], raw_result)
            text = raw_result.get("text")
            if not isinstance(text, str):
                raise ValueError("PaddleOCR cache text must be a string")
            confidence = raw_result.get("confidence")
            if not isinstance(confidence, int | float):
                raise ValueError("PaddleOCR cache confidence must be a number")
            bounding_box = raw_result.get("bounding_box")
            if not isinstance(bounding_box, Mapping):
                raise ValueError("PaddleOCR cache bounding box must be an object")
            bounding_box = cast(Mapping[str, object], bounding_box)

            points: dict[str, tuple[float, float]] = {}
            for key in ("top_left", "top_right", "bottom_right", "bottom_left"):
                points[key] = self._deserialize_point(bounding_box.get(key))
            results.append(
                PaddleOcrTextResult(
                    text=text,
                    confidence=float(confidence),
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
    def _deserialize_point(payload: object) -> tuple[float, float]:
        """Deserialize and validate a cached bounding-box point.

        Arguments:
            payload: decoded JSON point payload
        Returns:
            normalized x and y coordinates
        """
        if isinstance(payload, Mapping):
            point = cast(Mapping[str, object], payload)
            x = point.get("x")
            y = point.get("y")
        elif isinstance(payload, Sequence) and not isinstance(payload, str | bytes):
            if len(payload) != 2:
                raise ValueError("PaddleOCR cache points must contain two numbers")
            x, y = payload
        else:
            raise ValueError("PaddleOCR cache points must be arrays or objects")
        if not isinstance(x, int | float) or not isinstance(y, int | float):
            raise ValueError("PaddleOCR cache point coordinates must be numbers")
        return float(x), float(y)

    def _serialize(self, result: list[PaddleOcrTextResult]) -> object:
        """Serialize normalized PaddleOCR results.

        Arguments:
            result: normalized PaddleOCR results
        Returns:
            JSON-serializable payload
        """
        return [asdict(text_result) for text_result in result]
