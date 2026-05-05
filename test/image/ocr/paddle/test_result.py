#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of PaddleOCR result processing."""

from __future__ import annotations

from scinoephile.image.ocr.paddle import (
    PaddleOcrBoundingBox,
    PaddleOcrPoint,
    PaddleOcrTextResult,
    format_paddle_ocr_text,
)


def test_format_paddle_ocr_text_orders_results_into_lines():
    """Test OCR result formatting orders text top-to-bottom and left-to-right."""
    results = [
        _result("Bottom right", 80, 80),
        _result("Top right", 80, 10),
        _result("Bottom left", 10, 80),
        _result("Top left", 10, 10),
    ]

    text = format_paddle_ocr_text(results)

    assert text == "Top left Top right\\NBottom left Bottom right"


def _result(text: str, left: float, top: float) -> PaddleOcrTextResult:
    """Build a Paddle OCR text result.

    Arguments:
        text: recognized text
        left: left coordinate
        top: top coordinate
    Returns:
        text result
    """
    return PaddleOcrTextResult(
        text=text,
        confidence=0.95,
        bounding_box=PaddleOcrBoundingBox(
            top_left=PaddleOcrPoint(left, top),
            top_right=PaddleOcrPoint(left + 40, top),
            bottom_right=PaddleOcrPoint(left + 40, top + 20),
            bottom_left=PaddleOcrPoint(left, top + 20),
        ),
    )
