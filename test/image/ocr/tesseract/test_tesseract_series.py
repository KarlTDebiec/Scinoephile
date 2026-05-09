#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR image series processing."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.image.ocr.tesseract import (
    TesseractOcrRecognizer,
    ocr_image_series_with_tesseract,
)
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


class FakeTesseractRecognizer(TesseractOcrRecognizer):
    """Fake Tesseract recognizer for tests."""

    def __init__(self, texts: list[str]):
        """Initialize.

        Arguments:
            texts: texts to return from subsequent recognitions
        """
        self.texts = texts
        self.images: list[Image.Image] = []

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        self.images.append(image)
        return self.texts.pop(0)


def test_ocr_image_series_with_tesseract_preserves_timings_and_sets_text():
    """Test Tesseract image series processing preserves timings and text."""
    image_series = ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("RGBA", (10, 8), (255, 255, 255, 0)),
            ),
            ImageSubtitle(
                start=3000,
                end=4000,
                img=Image.new("RGBA", (12, 9), (255, 255, 255, 0)),
            ),
        ]
    )
    recognizer = FakeTesseractRecognizer(["first", "second"])

    text_series = ocr_image_series_with_tesseract(
        image_series,
        recognizer=recognizer,
    )

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    assert [image.size for image in recognizer.images] == [(10, 8), (12, 9)]


def test_ocr_image_series_with_tesseract_uses_runtime_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test Tesseract image series processing uses runtime cache by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    cache_dir_path = tmp_path / "cache"
    observed_cache_dir_paths = []
    observed_cache_namespaces = []

    class FakeDefaultRecognizer(FakeTesseractRecognizer):
        """Fake default recognizer with cache directory tracking."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | None = None,
            executable_path: Path | str = "tesseract",
            detect_italics: bool = False,
            language: str = "eng",
            legacy_tessdata_dir_path: Path | None = None,
            oem: int = 3,
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
                language: Tesseract language code
                legacy_tessdata_dir_path: optional tessdata directory for legacy OCR
                oem: Tesseract OCR engine mode
                psm: Tesseract page segmentation mode
                scale: image preprocessing scale
                skip_executable_validation: whether to skip executable validation
                tessdata_dir_path: optional tessdata directory
            """
            _ = (
                executable_path,
                detect_italics,
                legacy_tessdata_dir_path,
                oem,
                psm,
                scale,
                skip_executable_validation,
                tessdata_dir_path,
            )
            super().__init__([language])
            observed_cache_dir_paths.append(cache_dir_path)

    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.get_runtime_cache_dir_path",
        lambda *parts: observed_cache_namespaces.extend(parts) or cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractOcrRecognizer",
        FakeDefaultRecognizer,
    )
    image_series = ImageSeries(
        events=[
            ImageSubtitle(
                start=1000,
                end=2000,
                img=Image.new("RGBA", (10, 8), (255, 255, 255, 0)),
            ),
        ]
    )

    text_series = ocr_image_series_with_tesseract(image_series, language="eng")

    assert [event.text for event in text_series] == ["eng"]
    assert observed_cache_dir_paths == [cache_dir_path]
    assert observed_cache_namespaces == ["tesseract"]
