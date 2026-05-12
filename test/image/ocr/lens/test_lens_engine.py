#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Google Lens OCR recognition engine."""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from PIL import Image

import scinoephile.image.ocr.lens.google_lens_recognizer as lens_module
from scinoephile.image.ocr.lens.google_lens_recognizer import GoogleLensRecognizer


class CountingGoogleLensRecognizer(GoogleLensRecognizer):
    """Google Lens recognizer that counts uncached predictions."""

    def __init__(self, cache_dir_path: Path | None = None):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
        """
        self.cache_dir_path = cache_dir_path
        self.language = "en"
        self.predict_count = 0

    async def _recognize_image_uncached(self, image: Image.Image) -> list[str]:
        """Run fake Google Lens recognition.

        Arguments:
            image: input image
        Returns:
            normalized OCR lines
        """
        self.predict_count += 1
        return ["cached", "text"]


def test_clean_google_lens_text_ignores_empty_and_error_messages():
    """Test Google Lens text cleanup suppresses non-subtitle messages."""
    text = GoogleLensRecognizer._clean_text(
        "No OCR text found.\nRequest error (possibly proxy-related)\n"
    )

    assert text == ""


def test_clean_google_lens_text_joins_standalone_dash_and_ellipsis():
    """Test SubtitleEdit GoogleLensSharp line cleanup rules."""
    text = GoogleLensRecognizer._clean_text("-\nHello\n...\nworld")

    assert text == "- Hello ...\nworld"


def test_normalize_lens_result_falls_back_to_ocr_text_lines():
    """Test normalization falls back to full OCR text lines."""
    result = {"ocr_text": "full\ntext", "line_blocks": []}

    lines = GoogleLensRecognizer._normalize_lens_result(result)

    assert lines == ["full", "text"]


def test_normalize_lens_result_prefers_line_blocks():
    """Test normalization prefers line block text when available."""
    result: dict[str, Any] = {
        "ocr_text": "fallback",
        "line_blocks": [
            {"text": "first"},
            {"text": "second"},
        ],
    }

    lines = GoogleLensRecognizer._normalize_lens_result(result)

    assert lines == ["first", "second"]


def test_normalize_lens_result_supports_object_results():
    """Test normalization supports object-like chrome-lens-py results."""
    result = SimpleNamespace(
        ocr_text="fallback",
        line_blocks=[
            SimpleNamespace(text="first"),
            SimpleNamespace(text="second"),
        ],
    )

    lines = GoogleLensRecognizer._normalize_lens_result(result)

    assert lines == ["first", "second"]


def test_google_lens_recognizer_caches_results_by_image(tmp_path: Path):
    """Test Google Lens recognizer caches OCR results by image content."""
    recognizer = CountingGoogleLensRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached\ntext"
    assert recognizer.recognize_image(image) == "cached\ntext"

    assert recognizer.predict_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_google_lens_recognizer_formats_cached_results(tmp_path: Path):
    """Test cached Google Lens results are formatted after loading."""
    recognizer = CountingGoogleLensRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached\ntext"

    cache_path = next(tmp_path.glob("*.json"))
    cache_path.write_text(
        '{"lines": ["cached", "..."]}',
        encoding="utf-8",
    )

    assert recognizer.recognize_image(image) == "cached ..."
    assert recognizer.predict_count == 1


def test_google_lens_recognizer_does_not_cache_request_errors(tmp_path: Path):
    """Test transient Google Lens request errors are not cached as empty OCR."""

    class RequestErrorRecognizer(CountingGoogleLensRecognizer):
        """Google Lens recognizer that returns a request error."""

        async def _recognize_image_uncached(self, image: Image.Image) -> list[str]:
            """Run fake Google Lens recognition.

            Arguments:
                image: input image
            Returns:
                normalized OCR lines
            """
            self.predict_count += 1
            return ["Request error (possibly proxy-related)"]

    recognizer = RequestErrorRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    with pytest.raises(RuntimeError, match="Google Lens request error"):
        recognizer.recognize_image(image)

    assert recognizer.predict_count == 1
    assert not list(tmp_path.glob("*.json"))


def test_google_lens_recognizer_rejects_uncached_calls_in_async_loop(
    tmp_path: Path,
):
    """Test uncached synchronous recognition fails clearly in an async loop.

    Arguments:
        tmp_path: temporary path fixture
    """
    recognizer = CountingGoogleLensRecognizer(cache_dir_path=tmp_path)

    async def recognize() -> None:
        """Run synchronous recognition from an async context."""
        with pytest.raises(RuntimeError, match="cannot run uncached Google Lens OCR"):
            recognizer.recognize_image(Image.new("RGBA", (10, 8), (255, 255, 255, 0)))

    asyncio.run(recognize())


def test_google_lens_recognizer_import_error_is_actionable(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test missing chrome-lens-py dependency produces an actionable error.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    real_import = __import__

    def fake_import(
        name: str,
        globals_: Mapping[str, object] | None = None,
        locals_: Mapping[str, object] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> object:
        """Fake import that treats chrome-lens-py as missing.

        Arguments:
            name: module name
            globals_: global namespace
            locals_: local namespace
            fromlist: names to import
            level: import level
        Returns:
            imported module
        Raises:
            ImportError: if importing chrome_lens_py
        """
        if name == "chrome_lens_py":
            raise ImportError("missing chrome-lens-py")
        return real_import(name, globals_, locals_, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ImportError, match="chrome-lens-py"):
        GoogleLensRecognizer._get_lens_api_class()


def test_google_lens_recognizer_does_not_cache_lens_api_globally():
    """Test chrome-lens-py imports rely on Python's import cache."""
    assert not hasattr(lens_module, "LensAPI")


def test_google_lens_recognizer_reuses_lens_api_client(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test Google Lens recognizer reuses one LensAPI client.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    init_count = 0

    class FakeLensApi:
        """Fake chrome-lens-py LensAPI class."""

        def __init__(self):
            """Initialize."""
            nonlocal init_count
            init_count += 1

        async def process_image(self, **kwargs: object) -> dict[str, object]:
            """Process an image.

            Arguments:
                **kwargs: process image keyword arguments
            Returns:
                fake LensAPI result
            """
            return {"ocr_text": "recognized"}

    chrome_lens_py = ModuleType("chrome_lens_py")
    setattr(chrome_lens_py, "LensAPI", FakeLensApi)
    monkeypatch.setitem(sys.modules, "chrome_lens_py", chrome_lens_py)
    recognizer = GoogleLensRecognizer()

    assert recognizer.recognize_image(Image.new("RGBA", (10, 8))) == "recognized"
    assert recognizer.recognize_image(Image.new("RGBA", (12, 9))) == "recognized"

    assert init_count == 1
