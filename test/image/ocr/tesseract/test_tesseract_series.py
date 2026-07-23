#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR image series processing."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pytest import LogCaptureFixture, MonkeyPatch, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.tesseract import (
    ocr_image_series_with_tesseract,
)
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from test.helpers import parametrize
from test.helpers.ocr_recognizers import FailingOcrRecognizer, RecordingOcrRecognizer


def test_ocr_image_series_with_tesseract_preserves_timings_and_sets_text(
    monkeypatch: MonkeyPatch,
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
    RecordingOcrRecognizer.reset("first", "second")
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        RecordingOcrRecognizer,
    )

    text_series = ocr_image_series_with_tesseract(image_series)

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    recognizer = RecordingOcrRecognizer.instances[0]
    assert [image.size for image in recognizer.images] == [(10, 8), (12, 9)]


def test_ocr_image_series_with_tesseract_logs_progress(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
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
    RecordingOcrRecognizer.reset("first", "second")
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        RecordingOcrRecognizer,
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
    monkeypatch: MonkeyPatch,
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
    RecordingOcrRecognizer.reset(Language.eng.code)

    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.get_runtime_cache_dir_path",
        lambda *parts: observed_cache_namespaces.extend(parts) or cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        RecordingOcrRecognizer,
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
    recognizer = RecordingOcrRecognizer.instances[0]
    observed_cache_dir_paths.append(recognizer.kwargs["cache_dir_path"])
    assert observed_cache_dir_paths == [cache_dir_path]
    assert observed_cache_namespaces == ["tesseract"]
    assert recognizer.kwargs["executable_path"] == "custom-tesseract"
    assert recognizer.kwargs["detect_italics"] is True
    assert recognizer.kwargs["language"] is Language.eng
    assert recognizer.kwargs["oem"] is None
    assert recognizer.kwargs["psm"] == 7
    assert recognizer.kwargs["scale"] == 3
    assert recognizer.kwargs["skip_executable_validation"] is True
    assert recognizer.kwargs["tessdata_dir_path"] == tessdata_dir_path


@parametrize(
    "exception",
    [
        ImportError("missing tesseract dependency"),
        OSError("cache read failed"),
        RuntimeError("tesseract request failed"),
        ValueError("invalid tesseract response"),
    ],
)
def test_ocr_image_series_with_tesseract_wraps_processing_errors(
    monkeypatch: MonkeyPatch,
    exception: Exception,
):
    """Test Tesseract image series processing wraps implementation errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        exception: implementation exception raised during OCR
    """
    FailingOcrRecognizer.exception = exception
    monkeypatch.setattr(
        "scinoephile.image.ocr.tesseract.TesseractRecognizer",
        FailingOcrRecognizer,
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

    with raises(
        ScinoephileError,
        match="Unable to OCR image series with Tesseract",
    ) as excinfo:
        ocr_image_series_with_tesseract(image_series)

    assert excinfo.value.__cause__ is exception
