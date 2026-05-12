#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Google Lens OCR image series processing."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scinoephile.image.ocr.lens import (
    GoogleLensRecognizer,
    ocr_image_series_with_lens,
)
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


class FakeRecognizer(GoogleLensRecognizer):
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

    class FakeDefaultRecognizer(FakeRecognizer):
        """Fake default recognizer with cache directory tracking."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | None = None,
            language: str = "en",
        ):
            """Initialize.

            Arguments:
                cache_dir_path: directory in which to cache OCR results
                language: Google Lens OCR language code
            """
            super().__init__([language])
            observed_cache_dir_paths.append(cache_dir_path)

    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.get_runtime_cache_dir_path",
        lambda *parts: cache_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.GoogleLensRecognizer",
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
        language="zh-CN",
    )

    assert [event.text for event in text_series] == ["zh-CN"]
    assert observed_cache_dir_paths == [cache_dir_path]
