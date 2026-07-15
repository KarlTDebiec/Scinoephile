#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Google Lens OCR image series processing."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pytest import LogCaptureFixture, MonkeyPatch, raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.lens import ocr_image_series_with_lens
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle
from test.helpers import parametrize
from test.helpers.ocr_recognizers import FailingOcrRecognizer, RecordingOcrRecognizer


def test_ocr_image_series_with_lens_preserves_timings_and_sets_text(
    monkeypatch: MonkeyPatch,
):
    """Test Google Lens image series processing preserves timings and text.

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
        "scinoephile.image.ocr.lens.LensRecognizer",
        RecordingOcrRecognizer,
    )

    text_series = ocr_image_series_with_lens(image_series)

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    recognizer = RecordingOcrRecognizer.instances[0]
    assert [image.size for image in recognizer.images] == [(10, 8), (12, 9)]


def test_ocr_image_series_with_lens_logs_progress(
    caplog: LogCaptureFixture,
    monkeypatch: MonkeyPatch,
):
    """Test Google Lens image series processing logs OCR progress.

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
        "scinoephile.image.ocr.lens.LensRecognizer",
        RecordingOcrRecognizer,
    )

    with caplog.at_level("INFO", logger="scinoephile.image.ocr.lens"):
        ocr_image_series_with_lens(image_series)

    assert [
        record.message
        for record in caplog.records
        if record.name == "scinoephile.image.ocr.lens"
    ] == [
        "OCRing subtitle 1/2 with Google Lens",
        "OCRing subtitle 2/2 with Google Lens",
    ]


def test_ocr_image_series_with_lens_uses_runtime_cache(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test Google Lens image series processing uses runtime cache by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    cache_dir_path = tmp_path / "cache"
    RecordingOcrRecognizer.reset(Language.zho_hans.code)

    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.get_runtime_cache_dir_path",
        lambda *parts: cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.LensRecognizer",
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

    text_series = ocr_image_series_with_lens(
        image_series,
        language=Language.zho_hans,
        retries=5,
    )

    assert [event.text for event in text_series] == ["zho-Hans"]
    recognizer = RecordingOcrRecognizer.instances[0]
    assert recognizer.kwargs["cache_dir_path"] == cache_dir_path
    assert recognizer.kwargs["language"] is Language.zho_hans
    assert recognizer.kwargs["retries"] == 5


@parametrize(
    "exception",
    [
        ImportError("missing lens dependency"),
        NotADirectoryError("invalid cache directory"),
        OSError("cache read failed"),
        RuntimeError("lens request failed"),
        ValueError("invalid lens response"),
    ],
)
def test_ocr_image_series_with_lens_wraps_processing_errors(
    monkeypatch: MonkeyPatch,
    exception: Exception,
):
    """Test Lens image series processing wraps implementation errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        exception: implementation exception raised during OCR
    """
    FailingOcrRecognizer.exception = exception
    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.LensRecognizer",
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
        match="Unable to OCR image series with Google Lens",
    ) as excinfo:
        ocr_image_series_with_lens(image_series)

    assert excinfo.value.__cause__ is exception
