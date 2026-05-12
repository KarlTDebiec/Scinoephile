#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of PaddleOCR recognition engine."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np
import pytest
from PIL import Image

from scinoephile.image.ocr.paddle import PaddleOcrRecognizer
from scinoephile.image.ocr.paddle.bounding_box import PaddleOcrBoundingBox
from scinoephile.image.ocr.paddle.text_result import PaddleOcrTextResult


class CountingPaddleOcrRecognizer(PaddleOcrRecognizer):
    """PaddleOCR recognizer that counts uncached predictions."""

    def __init__(self, cache_dir_path: Path | None = None):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
        """
        self.language = "en"
        self.min_confidence = 0.0
        self.cache_dir_path = cache_dir_path
        self.predict_count = 0
        self._ocr = self

    def predict(self, array: np.ndarray) -> list[dict[str, Any]]:
        """Run fake PaddleOCR prediction.

        Arguments:
            array: RGB image array
        Returns:
            raw PaddleOCR results
        """
        self.predict_count += 1
        return [
            {
                "rec_texts": ["cached text"],
                "rec_scores": [0.95],
                "rec_polys": np.array([[[0, 0], [80, 0], [80, 20], [0, 20]]]),
            }
        ]


def test_paddle_ocr_recognizer_caches_results_by_image(tmp_path: Path):
    """Test PaddleOCR recognizer caches OCR results by image content."""
    recognizer = CountingPaddleOcrRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached text"
    assert recognizer.recognize_image(image) == "cached text"

    assert recognizer.predict_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_paddle_ocr_recognizer_uses_server_models(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test PaddleOCR recognizer hardcodes PP-OCRv5 server models.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    observed_kwargs = {}

    class FakePaddleOCR:
        """Fake PaddleOCR implementation."""

        def __init__(self, **kwargs: str | bool):
            """Initialize.

            Arguments:
                **kwargs: PaddleOCR keyword arguments
            """
            observed_kwargs.update(kwargs)

    paddleocr = ModuleType("paddleocr")
    setattr(paddleocr, "PaddleOCR", FakePaddleOCR)
    monkeypatch.setitem(sys.modules, "paddleocr", paddleocr)

    PaddleOcrRecognizer(language="ch")

    assert observed_kwargs["text_detection_model_name"] == "PP-OCRv5_server_det"
    assert observed_kwargs["text_recognition_model_name"] == "PP-OCRv5_server_rec"


def test_paddle_ocr_recognizer_imports_paddleocr_only_when_needed():
    """Test importing PaddleOCR recognizer does not import paddleocr."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scinoephile.image.ocr.paddle.paddle_ocr_recognizer;"
                "raise SystemExit('paddleocr' in sys.modules)"
            ),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_paddle_ocr_recognizer_rejects_unsupported_languages():
    """Test PaddleOCR recognizer only supports English and Chinese."""
    with pytest.raises(ValueError, match="PaddleOCR language must be one of"):
        PaddleOcrRecognizer(language="korean")


def test_format_paddle_ocr_text_orders_results_into_lines():
    """Test OCR result formatting orders text top-to-bottom and left-to-right."""
    results = [
        _result("Bottom right", 80, 80),
        _result("Top right", 80, 10),
        _result("Bottom left", 10, 80),
        _result("Top left", 10, 10),
    ]

    text = PaddleOcrRecognizer._format_paddle_ocr_text(results)

    assert text == "Top left Top right\\NBottom left Bottom right"


def test_normalize_paddle_ocr_results_parses_paddleocr3_result_dict():
    """Test PaddleOCR 3 result dictionaries are normalized."""
    raw_results = [
        {
            "rec_texts": ["left", "right"],
            "rec_scores": [0.95, 0.9],
            "rec_polys": np.array(
                [
                    [[0, 0], [40, 0], [40, 20], [0, 20]],
                    [[50, 0], [90, 0], [90, 20], [50, 20]],
                ]
            ),
        }
    ]

    results = PaddleOcrRecognizer._normalize_paddle_ocr_results(raw_results)

    assert [(result.text, result.confidence) for result in results] == [
        ("left", 0.95),
        ("right", 0.9),
    ]
    assert results[1].bounding_box.top_left[0] == 50


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
            top_left=(left, top),
            top_right=(left + 40, top),
            bottom_right=(left + 40, top + 20),
            bottom_left=(left, top + 20),
        ),
    )
