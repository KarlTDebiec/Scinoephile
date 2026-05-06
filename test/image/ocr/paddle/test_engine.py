#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of PaddleOCR recognition engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from scinoephile.image.ocr.paddle import PaddleOcrRecognizer


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

    def _predict(self, array: np.ndarray) -> Any:
        """Run fake PaddleOCR prediction.

        Arguments:
            array: RGB image array
        Returns:
            raw PaddleOCR results
        """
        self.predict_count += 1
        return [
            [
                [[0, 0], [80, 0], [80, 20], [0, 20]],
                ("cached text", 0.95),
            ]
        ]


def test_paddle_ocr_recognizer_caches_results_by_image(tmp_path: Path):
    """Test PaddleOCR recognizer caches OCR results by image content."""
    recognizer = CountingPaddleOcrRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached text"
    assert recognizer.recognize_image(image) == "cached text"

    assert recognizer.predict_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1
