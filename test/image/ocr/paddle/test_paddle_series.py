#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of PaddleOCR image series processing."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pytest import LogCaptureFixture, MonkeyPatch, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.paddle import ocr_image_series_with_paddle
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from test.helpers import parametrize
from test.helpers.ocr_recognizers import FailingOcrRecognizer, RecordingOcrRecognizer


def test_ocr_image_series_with_paddle_preserves_timings_and_sets_text(
    monkeypatch: MonkeyPatch,
):
    """Test PaddleOCR image series processing preserves timings and writes text.

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
        "scinoephile.image.ocr.paddle.PaddleRecognizer",
        RecordingOcrRecognizer,
    )

    text_series = ocr_image_series_with_paddle(image_series)

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    recognizer = RecordingOcrRecognizer.instances[0]
    assert [image.size for image in recognizer.images] == [(50, 48), (52, 49)]


def test_ocr_image_series_with_paddle_logs_progress(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    """Test PaddleOCR image series processing logs OCR progress.

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
        "scinoephile.image.ocr.paddle.PaddleRecognizer",
        RecordingOcrRecognizer,
    )

    with caplog.at_level("INFO", logger="scinoephile.image.ocr.paddle"):
        ocr_image_series_with_paddle(image_series)

    assert [
        record.message
        for record in caplog.records
        if record.name == "scinoephile.image.ocr.paddle"
    ] == [
        "OCRing subtitle 1/2 with PaddleOCR",
        "OCRing subtitle 2/2 with PaddleOCR",
    ]


def test_ocr_image_series_with_paddle_uses_runtime_cache(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test PaddleOCR image series processing uses the runtime cache by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    cache_dir_path = tmp_path / "cache"
    RecordingOcrRecognizer.reset(Language.zho_hans.code)

    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.get_runtime_cache_dir_path",
        lambda *parts: cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.PaddleRecognizer",
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

    text_series = ocr_image_series_with_paddle(
        image_series,
        language=Language.zho_hans,
        min_confidence=0.8,
    )

    assert [event.text for event in text_series] == ["zho-Hans"]
    recognizer = RecordingOcrRecognizer.instances[0]
    assert recognizer.kwargs["cache_dir_path"] == cache_dir_path
    assert recognizer.kwargs["language"] is Language.zho_hans
    assert recognizer.kwargs["min_confidence"] == 0.8


@parametrize(
    "exception",
    [
        ImportError("missing paddle dependency"),
        OSError("cache read failed"),
        RuntimeError("paddle request failed"),
        ValueError("invalid paddle response"),
    ],
)
def test_ocr_image_series_with_paddle_wraps_processing_errors(
    monkeypatch: MonkeyPatch,
    exception: Exception,
):
    """Test PaddleOCR image series processing wraps implementation errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        exception: implementation exception raised during OCR
    """
    FailingOcrRecognizer.exception = exception
    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.PaddleRecognizer",
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
        match="Unable to OCR image series with PaddleOCR",
    ) as excinfo:
        ocr_image_series_with_paddle(image_series)

    assert excinfo.value.__cause__ is exception
