#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR image series processing."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.tesseract import (
    ocr_image_series_with_tesseract,
)
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


class FakeTesseractRecognizer:
    """Fake Tesseract recognizer for tests."""

    texts: list[str] = []
    """Texts to return from subsequent recognitions."""

    instances: list[FakeTesseractRecognizer] = []
    """Fake recognizer instances created by the OCR helper."""

    def __init__(
        self,
        *,
        cache_dir_path: Path | None = None,
        executable_path: Path | str = "tesseract",
        detect_italics: bool = False,
        language: Language = Language.eng,
        oem: int | None = 3,
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
            language: Scinoephile language
            oem: Tesseract OCR engine mode
            psm: Tesseract page segmentation mode
            scale: image preprocessing scale
            skip_executable_validation: whether to skip executable validation
            tessdata_dir_path: optional tessdata directory
        """
        self.cache_dir_path = cache_dir_path
        self.executable_path = executable_path
        self.detect_italics = detect_italics
        self.language = language
        self.oem = oem
        self.psm = psm
        self.scale = scale
        self.skip_executable_validation = skip_executable_validation
        self.tessdata_dir_path = tessdata_dir_path
        self.texts = list(type(self).texts)
        self.images: list[Image.Image] = []
        type(self).instances.append(self)

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        self.images.append(image)
        return self.texts.pop(0)


class FailingTesseractRecognizer:
    """Fake Tesseract recognizer that raises a configured exception."""

    exception: Exception | None = None
    """Exception raised during recognition."""

    def __init__(self, **kwargs: object):
        """Initialize.

        Arguments:
            **kwargs: ignored recognizer keyword arguments
        """
        _ = kwargs

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Raises:
            Exception: configured exception
        """
        _ = image
        if self.exception is None:
            raise AssertionError(
                "FailingTesseractRecognizer.exception must be configured"
            )
        raise self.exception


def test_ocr_image_series_with_tesseract_preserves_timings_and_sets_text(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test Tesseract image series processing preserves timings and text.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
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
    FakeTesseractRecognizer.texts = ["first", "second"]
    FakeTesseractRecognizer.instances = []
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        FakeTesseractRecognizer,
    )

    text_series = ocr_image_series_with_tesseract(image_series)

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    recognizer = FakeTesseractRecognizer.instances[0]
    assert [image.size for image in recognizer.images] == [(10, 8), (12, 9)]


def test_ocr_image_series_with_tesseract_logs_progress(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test Tesseract image series processing logs OCR progress.

    Arguments:
        caplog: pytest log capture fixture
        monkeypatch: pytest monkeypatch fixture
    """
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
    FakeTesseractRecognizer.texts = ["first", "second"]
    FakeTesseractRecognizer.instances = []
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        FakeTesseractRecognizer,
    )

    with caplog.at_level("INFO", logger="scinoephile.image.ocr.tesseract"):
        ocr_image_series_with_tesseract(image_series)

    assert [
        record.message
        for record in caplog.records
        if record.name == "scinoephile.image.ocr.tesseract"
    ] == [
        "OCRing subtitle 1/2 with Tesseract",
        "OCRing subtitle 2/2 with Tesseract",
    ]


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
    tessdata_dir_path = tmp_path / "tessdata"
    observed_cache_dir_paths = []
    observed_cache_namespaces = []
    FakeTesseractRecognizer.texts = [Language.eng.tag]
    FakeTesseractRecognizer.instances = []

    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.get_runtime_cache_dir_path",
        lambda *parts: observed_cache_namespaces.extend(parts) or cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        FakeTesseractRecognizer,
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

    text_series = ocr_image_series_with_tesseract(
        image_series,
        executable_path="custom-tesseract",
        detect_italics=True,
        language=Language.eng,
        oem=None,
        psm=7,
        scale=3,
        skip_executable_validation=True,
        tessdata_dir_path=tessdata_dir_path,
    )

    assert [event.text for event in text_series] == ["eng"]
    recognizer = FakeTesseractRecognizer.instances[0]
    observed_cache_dir_paths.append(recognizer.cache_dir_path)
    assert observed_cache_dir_paths == [cache_dir_path]
    assert observed_cache_namespaces == ["tesseract"]
    assert recognizer.executable_path == "custom-tesseract"
    assert recognizer.detect_italics is True
    assert recognizer.language is Language.eng
    assert recognizer.oem is None
    assert recognizer.psm == 7
    assert recognizer.scale == 3
    assert recognizer.skip_executable_validation is True
    assert recognizer.tessdata_dir_path == tessdata_dir_path


@pytest.mark.parametrize(
    "exception",
    [
        ImportError("missing tesseract dependency"),
        OSError("cache read failed"),
        RuntimeError("tesseract request failed"),
        ValueError("invalid tesseract response"),
    ],
)
def test_ocr_image_series_with_tesseract_wraps_processing_errors(
    monkeypatch: pytest.MonkeyPatch,
    exception: Exception,
):
    """Test Tesseract image series processing wraps implementation errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        exception: implementation exception raised during OCR
    """
    FailingTesseractRecognizer.exception = exception
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        FailingTesseractRecognizer,
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

    with pytest.raises(
        ScinoephileError,
        match="Unable to OCR image series with Tesseract",
    ) as excinfo:
        ocr_image_series_with_tesseract(image_series)

    assert excinfo.value.__cause__ is exception
