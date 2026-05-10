#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Google Lens OCR recognition engine."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
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
        self.api_key = None
        self.cache_dir_path = cache_dir_path
        self.client_region = None
        self.client_time_zone = None
        self.language = "en"
        self.max_concurrent = 5
        self.proxy = None
        self.timeout = 60
        self.predict_count = 0

    async def _recognize_image_uncached(self, image: Image.Image) -> str:
        """Run fake Google Lens recognition.

        Arguments:
            image: input image
        Returns:
            recognized text
        """
        self.predict_count += 1
        return "cached text"


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


def test_extract_text_falls_back_to_ocr_text():
    """Test extraction falls back to full OCR text."""
    result = {"ocr_text": "full\ntext", "line_blocks": []}

    text = GoogleLensRecognizer._extract_text(result)

    assert text == "full\ntext"


def test_extract_text_prefers_line_blocks():
    """Test extraction joins line block text when available."""
    result: dict[str, Any] = {
        "ocr_text": "fallback",
        "line_blocks": [
            {"text": "first"},
            {"text": "second"},
        ],
    }

    text = GoogleLensRecognizer._extract_text(result)

    assert text == "first\nsecond"


def test_google_lens_recognizer_caches_results_by_image(tmp_path: Path):
    """Test Google Lens recognizer caches OCR results by image content."""
    recognizer = CountingGoogleLensRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached text"
    assert recognizer.recognize_image(image) == "cached text"

    assert recognizer.predict_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


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

    monkeypatch.setattr(lens_module, "LensAPI", None)
    monkeypatch.setattr("builtins.__import__", fake_import)

    with pytest.raises(ImportError, match="chrome-lens-py"):
        GoogleLensRecognizer._get_lens_api_class()
