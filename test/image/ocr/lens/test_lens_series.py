#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Google Lens OCR image series processing."""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

import scinoephile.image.ocr.lens as lens_ocr
from scinoephile.core import Language, ScinoephileError
from scinoephile.image.ocr.lens import ocr_image_series_with_lens
from scinoephile.image.subtitles import ImageSeries, ImageSubtitle


class FakeRecognizer:
    """Fake Google Lens recognizer for tests."""

    texts: list[str] = []
    """Texts to return from subsequent recognitions."""

    instances: list[FakeRecognizer] = []
    """Fake recognizer instances created by the OCR helper."""

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
        self.cache_dir_path = cache_dir_path
        self.language = language
        self.retries = retries
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


class FailingRecognizer:
    """Fake Google Lens recognizer that raises a configured exception."""

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
            raise AssertionError("FailingRecognizer.exception must be configured")
        raise self.exception


def test_lens_module_exposes_only_current_public_helpers():
    """Test Google Lens module no longer exposes removed helper functions."""
    assert not hasattr(lens_ocr, "get_lens_recognizer")
    assert not hasattr(lens_ocr, "get_lens_language_code")


def test_ocr_image_series_with_lens_preserves_timings_and_sets_text(
    monkeypatch: pytest.MonkeyPatch,
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
    FakeRecognizer.texts = ["first", "second"]
    FakeRecognizer.instances = []
    monkeypatch.setattr("scinoephile.image.ocr.lens.LensRecognizer", FakeRecognizer)

    text_series = ocr_image_series_with_lens(image_series)

    assert [(event.start, event.end, event.text) for event in text_series] == [
        (1000, 2000, "first"),
        (3000, 4000, "second"),
    ]
    recognizer = FakeRecognizer.instances[0]
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
    FakeRecognizer.texts = [Language.zho_hans.tag]
    FakeRecognizer.instances = []

    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.get_runtime_cache_dir_path",
        lambda *parts: cache_dir_path,
    )
    monkeypatch.setattr("scinoephile.image.ocr.lens.LensRecognizer", FakeRecognizer)
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
    recognizer = FakeRecognizer.instances[0]
    assert recognizer.cache_dir_path == cache_dir_path
    assert recognizer.language is Language.zho_hans
    assert recognizer.retries == 5


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
def test_ocr_image_series_with_lens_wraps_processing_errors(
    monkeypatch: pytest.MonkeyPatch,
    exception: Exception,
):
    """Test Lens image series processing wraps implementation errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        exception: implementation exception raised during OCR
    """
    FailingRecognizer.exception = exception
    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.LensRecognizer",
        FailingRecognizer,
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
        match="Unable to OCR image series with Google Lens",
    ) as excinfo:
        ocr_image_series_with_lens(image_series)

    assert excinfo.value.__cause__ is exception
