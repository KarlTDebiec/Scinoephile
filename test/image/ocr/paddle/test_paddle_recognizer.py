#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of PaddleOCR recognition engine."""

from __future__ import annotations

import logging
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import ModuleType
from typing import Any, cast

import numpy as np
from PIL import Image
from pytest import MonkeyPatch, raises

from scinoephile.common.subprocess import run_command
from scinoephile.core import Language
from scinoephile.image.ocr.paddle import PaddleRecognizer
from scinoephile.image.ocr.paddle.bounding_box import PaddleOcrBoundingBox
from scinoephile.image.ocr.paddle.text_result import PaddleOcrTextResult
from test.helpers import parametrize


class CountingPaddleRecognizer(PaddleRecognizer):
    """PaddleOCR recognizer that counts uncached predictions."""

    def __init__(self, cache_dir_path: Path | None = None):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
        """
        self.language = Language.eng
        self.paddle_language_code = "en"
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


def test_paddle_recognizer_caches_results_by_image(tmp_path: Path):
    """Test PaddleOCR recognizer caches OCR results by image content."""
    recognizer = CountingPaddleRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached text"
    assert recognizer.recognize_image(image) == "cached text"

    assert recognizer.predict_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_paddle_recognizer_uses_server_models_and_disables_mkldnn_on_windows(
    monkeypatch: MonkeyPatch,
):
    """Test PaddleOCR recognizer hardcodes server models and Windows MKL-DNN.

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
    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.paddle_recognizer.system",
        lambda: "Windows",
    )

    PaddleRecognizer(language=Language.zho_hans)

    assert observed_kwargs["lang"] == "ch"
    assert observed_kwargs["text_detection_model_name"] == "PP-OCRv5_server_det"
    assert observed_kwargs["text_recognition_model_name"] == "PP-OCRv5_server_rec"
    assert observed_kwargs["enable_mkldnn"] is False


def test_paddle_recognizer_keeps_mkldnn_enabled_off_windows(monkeypatch: MonkeyPatch):
    """Test PaddleOCR recognizer keeps MKL-DNN enabled off Windows.

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
    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.paddle_recognizer.system",
        lambda: "Linux",
    )

    PaddleRecognizer(language=Language.zho_hans)

    assert observed_kwargs["enable_mkldnn"] is True


def test_paddle_recognizer_preserves_root_logger_level(monkeypatch: MonkeyPatch):
    """Test PaddleOCR construction does not change root logging level.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """

    class FakePaddleOCR:
        """Fake PaddleOCR implementation that mutates root logging."""

        def __init__(self, **kwargs: object):
            """Initialize.

            Arguments:
                **kwargs: PaddleOCR keyword arguments
            """
            _ = kwargs
            logging.getLogger().setLevel(logging.WARNING)

    root_logger = logging.getLogger()
    previous_level = root_logger.level
    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.paddle_recognizer.PaddleRecognizer."
        "_import_paddleocr_paddle_ocr",
        staticmethod(lambda: FakePaddleOCR),
    )

    try:
        root_logger.setLevel(logging.INFO)

        PaddleRecognizer(language=Language.zho_hans)

        assert root_logger.level == logging.INFO
    finally:
        root_logger.setLevel(previous_level)


def test_paddle_recognizer_imports_paddleocr_only_when_needed():
    """Test importing PaddleOCR recognizer does not import paddleocr."""
    exitcode, _, _ = run_command(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scinoephile.image.ocr.paddle.paddle_recognizer;"
                "raise SystemExit('paddleocr' in sys.modules)"
            ),
        ],
    )

    assert exitcode == 0


def test_paddle_ocr_class_requires_ocr_extra(monkeypatch: MonkeyPatch):
    """Test PaddleOCR import errors mention the OCR extra."""
    real_import = __import__

    def fake_import(
        name: str,
        globals_: Mapping[str, object] | None = None,
        locals_: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        """Fake import that treats paddleocr as missing.

        Arguments:
            name: module name
            globals_: global namespace
            locals_: local namespace
            fromlist: names to import
            level: import level
        Returns:
            imported module
        Raises:
            ImportError: if importing paddleocr
        """
        if name == "paddleocr":
            raise ImportError("missing paddleocr")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with raises(ImportError, match="'ocr' extra"):
        PaddleRecognizer._import_paddleocr_paddle_ocr()


def test_paddle_recognizer_rejects_unsupported_languages():
    """Test PaddleOCR recognizer only supports English and Chinese."""
    with raises(ValueError, match="not supported by PaddleOCR"):
        PaddleRecognizer(language=cast(Language, "korean"))


@parametrize(
    ("language", "expected_code"),
    [
        (Language.eng, "en"),
        (Language.yue_hans, "ch"),
        (Language.yue_hant, "chinese_cht"),
        (Language.zho_hans, "ch"),
        (Language.zho_hant, "chinese_cht"),
    ],
)
def test_paddle_recognizer_maps_supported_languages_to_engine_codes(
    monkeypatch: MonkeyPatch,
    language: Language,
    expected_code: str,
):
    """Test PaddleOCR recognizer maps supported languages to engine codes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        language: language to use
        expected_code: expected PaddleOCR language code
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

    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.paddle_recognizer.PaddleRecognizer."
        "_import_paddleocr_paddle_ocr",
        staticmethod(lambda: FakePaddleOCR),
    )

    recognizer = PaddleRecognizer(language=language)

    assert recognizer.language is language
    assert recognizer.paddle_language_code == expected_code
    assert observed_kwargs["lang"] == expected_code


def test_format_paddle_ocr_text_orders_results_into_lines():
    """Test OCR result formatting orders text top-to-bottom and left-to-right."""
    results = [
        _result("Bottom right", 80, 80),
        _result("Top right", 80, 10),
        _result("Bottom left", 10, 80),
        _result("Top left", 10, 10),
    ]

    text = PaddleRecognizer._format_paddle_ocr_text(results)

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

    results = PaddleRecognizer._normalize_paddle_ocr_results(raw_results)

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
