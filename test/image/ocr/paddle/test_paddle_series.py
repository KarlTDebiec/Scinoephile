#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of PaddleOCR image series processing."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.paddle import (
    PaddleRecognizer,
    get_paddle_language_code,
    ocr_image_series_with_paddle,
)
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


class FakeRecognizer(PaddleRecognizer):
    """Fake PaddleOCR recognizer for tests."""

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


class FailingRecognizer(PaddleRecognizer):
    """Fake PaddleOCR recognizer that raises a configured exception."""

    def __init__(self, exception: Exception):
        """Initialize.

        Arguments:
            exception: exception to raise from recognition
        """
        self.exception = exception

    def recognize_image(self, image: Image.Image) -> str:
        """Recognize text from an image.

        Arguments:
            image: input image
        Raises:
            Exception: configured exception
        """
        _ = image
        raise self.exception


def test_ocr_image_series_with_paddle_preserves_timings_and_sets_text():
    """Test PaddleOCR image series processing preserves timings and writes text."""
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
    recognizer = FakeRecognizer(["first", "second"])

    text_series = ocr_image_series_with_paddle(
        image_series,
        recognizer=recognizer,
    )

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    assert [image.size for image in recognizer.images] == [(50, 48), (52, 49)]


def test_ocr_image_series_with_paddle_uses_runtime_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test PaddleOCR image series processing uses the runtime cache by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    cache_dir_path = tmp_path / "cache"
    observed_cache_dir_paths = []

    class FakeDefaultRecognizer(FakeRecognizer):
        """Fake default recognizer with cache directory tracking."""

        def __init__(
            self,
            *,
            language: Language,
            cache_dir_path: Path | None = None,
            min_confidence: float = 0.0,
        ):
            """Initialize.

            Arguments:
                language: Scinoephile language
                cache_dir_path: directory in which to cache OCR results
                min_confidence: minimum confidence to include
            """
            _ = min_confidence
            super().__init__([language.tag])
            observed_cache_dir_paths.append(cache_dir_path)

    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.get_runtime_cache_dir_path",
        lambda *parts: cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.paddle.PaddleRecognizer",
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

    text_series = ocr_image_series_with_paddle(image_series, language=Language.zho_hans)

    assert [event.text for event in text_series] == ["zho-Hans"]
    assert observed_cache_dir_paths == [cache_dir_path]


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        (Language.eng, "en"),
        (Language.zho_hans, "ch"),
        (Language.zho_hant, "chinese_cht"),
    ],
)
def test_get_paddle_language_code(language: Language, expected: str):
    """Test PaddleOCR language code selection.

    Arguments:
        language: Scinoephile language
        expected: expected PaddleOCR language code
    """
    assert get_paddle_language_code(language) == expected


@pytest.mark.parametrize(
    "exception",
    [
        ImportError("missing paddle dependency"),
        OSError("cache read failed"),
        RuntimeError("paddle request failed"),
        ValueError("invalid paddle response"),
    ],
)
def test_ocr_image_series_with_paddle_wraps_processing_errors(exception: Exception):
    """Test PaddleOCR image series processing wraps implementation errors.

    Arguments:
        exception: implementation exception raised during OCR
    """
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
        match="Unable to OCR image series with PaddleOCR",
    ) as excinfo:
        ocr_image_series_with_paddle(
            image_series,
            recognizer=FailingRecognizer(exception),
        )

    assert excinfo.value.__cause__ is exception
