#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Google Lens OCR image series processing."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.lens import (
    LensRecognizer,
    get_lens_language_code,
    ocr_image_series_with_lens,
)
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


class FakeRecognizer(LensRecognizer):
    """Fake Google Lens recognizer for tests."""

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


class FailingRecognizer(LensRecognizer):
    """Fake Google Lens recognizer that raises a configured exception."""

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


def test_ocr_image_series_with_lens_preserves_timings_and_sets_text():
    """Test Google Lens image series processing preserves timings and text."""
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

    text_series = ocr_image_series_with_lens(
        image_series,
        recognizer=recognizer,
    )

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    assert [image.size for image in recognizer.images] == [(10, 8), (12, 9)]


def test_ocr_image_series_with_lens_uses_runtime_cache(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test Google Lens image series processing uses runtime cache by default.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    cache_dir_path = tmp_path / "cache"
    observed_cache_dir_paths = []
    observed_retries = []

    class FakeDefaultRecognizer(FakeRecognizer):
        """Fake default recognizer with cache directory tracking."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | None = None,
            language: Language = Language.eng,
            retries: int = 3,
        ):
            """Initialize.

            Arguments:
                cache_dir_path: directory in which to cache OCR results
                language: Scinoephile language
                retries: Google Lens OCR request attempts per uncached image
            """
            super().__init__([language.tag])
            observed_cache_dir_paths.append(cache_dir_path)
            observed_retries.append(retries)

    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.get_runtime_cache_dir_path",
        lambda *parts: cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.LensRecognizer",
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

    text_series = ocr_image_series_with_lens(
        image_series,
        language=Language.zho_hans,
        retries=5,
    )

    assert [event.text for event in text_series] == ["zho-Hans"]
    assert observed_cache_dir_paths == [cache_dir_path]
    assert observed_retries == [5]


@pytest.mark.parametrize(
    "exception",
    [
        ImportError("missing lens dependency"),
        NotADirectoryError("invalid cache directory"),
        OSError("cache read failed"),
        RuntimeError("lens request failed"),
        ValueError("invalid lens response"),
    ],
)
def test_ocr_image_series_with_lens_wraps_processing_errors(exception: Exception):
    """Test Lens image series processing wraps implementation errors.

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
        match="Unable to OCR image series with Google Lens",
    ) as excinfo:
        ocr_image_series_with_lens(
            image_series,
            recognizer=FailingRecognizer(exception),
        )

    assert excinfo.value.__cause__ is exception


@pytest.mark.parametrize(
    ("language", "expected"),
    [
        (Language.eng, "en"),
        (Language.zho_hans, "zh-CN"),
        (Language.zho_hant, "zh-TW"),
    ],
)
def test_get_lens_language_code(language: Language, expected: str):
    """Test Google Lens language code selection.

    Arguments:
        language: Scinoephile language
        expected: expected Google Lens language code
    """
    assert get_lens_language_code(language) == expected
