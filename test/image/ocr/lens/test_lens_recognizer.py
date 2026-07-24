#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Google Lens OCR recognition engine."""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, cast

from PIL import Image
from pytest import MonkeyPatch, raises

from scinoephile.common.subprocess import run_command
from scinoephile.core import Language
from scinoephile.image.ocr.lens.lens_recognizer import LensRecognizer
from test.helpers import parametrize


class FakeLensApiError(RuntimeError):
    """Fake chrome-lens-py LensAPIError."""


class CountingLensRecognizer(LensRecognizer):
    """Google Lens recognizer that counts uncached predictions."""

    def __init__(
        self,
        cache_dir_path: Path | None = None,
        exceptions: list[Exception | None] | None = None,
        results: list[list[str]] | None = None,
    ):
        """Initialize.

        Arguments:
            cache_dir_path: directory in which to cache OCR results
            exceptions: exceptions to raise from subsequent recognitions
            results: normalized OCR lines to return from subsequent recognitions
        """
        self.cache_dir_path = cache_dir_path
        self.language = Language.eng
        self.lens_language_code = "en"
        self.retries = 3
        self.predict_count = 0
        self.exceptions = exceptions
        if results is None:
            results = [["cached", "text"]]
        self.results = results
        self._api = self
        self._lens_api_error_class = FakeLensApiError

    async def process_image(self, **kwargs: object) -> dict[str, object]:
        """Process an image.

        Arguments:
            **kwargs: process image keyword arguments
        Returns:
            fake LensAPI result
        """
        self.predict_count += 1
        if self.exceptions is not None:
            exception_index = min(self.predict_count - 1, len(self.exceptions) - 1)
            exception = self.exceptions[exception_index]
            if exception is not None:
                raise exception
        result_index = min(self.predict_count - 1, len(self.results) - 1)
        return {"ocr_text": "\n".join(self.results[result_index])}


def patch_google_lens_sleep(monkeypatch: MonkeyPatch) -> list[float]:
    """Patch Google Lens retry sleeps and capture their delays.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    Returns:
        captured sleep delays
    """
    delays = []

    async def fake_sleep(delay: float):
        """Capture retry sleep delay.

        Arguments:
            delay: requested sleep delay
        """
        delays.append(delay)

    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.lens_recognizer.asyncio.sleep",
        fake_sleep,
    )
    return delays


def test_clean_google_lens_text_ignores_empty_and_error_messages():
    """Test Google Lens text cleanup suppresses non-subtitle messages."""
    text = LensRecognizer._clean_text(
        "No OCR text found.\nRequest error (possibly proxy-related)\n"
    )

    assert text == ""


def test_clean_google_lens_text_joins_standalone_dash_and_ellipsis():
    """Test SubtitleEdit GoogleLensSharp line cleanup rules."""
    text = LensRecognizer._clean_text("-\nHello\n...\nworld")

    assert text == "- Hello ...\nworld"


def test_normalize_lens_result_falls_back_to_ocr_text_lines():
    """Test normalization falls back to full OCR text lines."""
    result = {"ocr_text": "full\ntext", "line_blocks": []}

    lines = LensRecognizer._normalize_lens_result(result)

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

    lines = LensRecognizer._normalize_lens_result(result)

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

    lines = LensRecognizer._normalize_lens_result(result)

    assert lines == ["first", "second"]


def test_lens_recognizer_rejects_unsupported_languages():
    """Test Google Lens recognizer only supports English and Chinese."""
    with raises(ValueError, match="not supported by Google Lens OCR"):
        LensRecognizer(language=cast(Language, "korean"))


@parametrize(
    ("language", "expected_code"),
    [
        (Language.eng, "en"),
        (Language.yue_hans, "zh-CN"),
        (Language.yue_hant, "zh-TW"),
        (Language.zho_hans, "zh-CN"),
        (Language.zho_hant, "zh-TW"),
    ],
)
def test_lens_recognizer_maps_supported_languages_to_engine_codes(
    monkeypatch: MonkeyPatch,
    language: Language,
    expected_code: str,
):
    """Test Google Lens recognizer maps supported languages to engine codes.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        language: language to use
        expected_code: expected Google Lens language code
    """

    class FakeLensApi:
        """Fake chrome-lens-py LensAPI class."""

    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.lens_recognizer.LensRecognizer."
        "_import_chrome_lens_py_lens_api",
        staticmethod(lambda: FakeLensApi),
    )
    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.lens_recognizer.LensRecognizer."
        "_import_chrome_lens_py_lens_api_error",
        staticmethod(lambda: FakeLensApiError),
    )

    recognizer = LensRecognizer(language=language)

    assert recognizer.language is language
    assert recognizer.lens_language_code == expected_code


def test_lens_recognizer_caches_results_by_image(tmp_path: Path):
    """Test Google Lens recognizer caches OCR results by image content."""
    recognizer = CountingLensRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached\ntext"
    assert recognizer.recognize_image(image) == "cached\ntext"

    assert recognizer.predict_count == 1
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_lens_recognizer_formats_cached_results(tmp_path: Path):
    """Test cached Google Lens results are formatted after loading."""
    recognizer = CountingLensRecognizer(cache_dir_path=tmp_path)
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "cached\ntext"

    cache_path = next(tmp_path.glob("*.json"))
    cache_path.write_text(
        '{"lines": ["cached", "..."]}',
        encoding="utf-8",
    )

    assert recognizer.recognize_image(image) == "cached ..."
    assert recognizer.predict_count == 1


def test_lens_recognizer_does_not_cache_request_errors(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test transient Google Lens request errors are not cached as empty OCR.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    patch_google_lens_sleep(monkeypatch)
    recognizer = CountingLensRecognizer(
        cache_dir_path=tmp_path,
        results=[["Request error (possibly proxy-related)"]],
    )
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    with raises(RuntimeError, match="Google Lens request error"):
        recognizer.recognize_image(image)

    assert recognizer.predict_count == 3
    assert not list(tmp_path.glob("*.json"))


def test_lens_recognizer_retries_request_errors_before_caching(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test Google Lens retries transient request errors before caching success.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    patch_google_lens_sleep(monkeypatch)
    recognizer = CountingLensRecognizer(
        cache_dir_path=tmp_path,
        results=[
            ["Request error (possibly proxy-related): 502 Bad Gateway"],
            ["Request error (possibly proxy-related): 502 Bad Gateway"],
            ["recognized"],
        ],
    )
    recognizer.retries = 3
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "recognized"

    assert recognizer.predict_count == 3
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_lens_recognizer_raises_last_request_error_after_retries(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
):
    """Test Google Lens raises the last request error after retry exhaustion.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: temporary path fixture
    """
    patch_google_lens_sleep(monkeypatch)
    recognizer = CountingLensRecognizer(
        cache_dir_path=tmp_path,
        results=[
            ["Request error (possibly proxy-related): attempt 1"],
            ["Request error (possibly proxy-related): attempt 2"],
            ["Request error (possibly proxy-related): attempt 3"],
        ],
    )
    recognizer.retries = 3
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    with raises(RuntimeError, match="attempt 3"):
        recognizer.recognize_image(image)

    assert recognizer.predict_count == 3
    assert not list(tmp_path.glob("*.json"))


def test_lens_recognizer_retries_in_one_asyncio_run(monkeypatch: MonkeyPatch):
    """Test Google Lens retries within one asyncio.run call.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    real_asyncio_run = asyncio.run
    run_count = 0
    patch_google_lens_sleep(monkeypatch)

    def counting_run(main: Any, **kwargs: Any) -> Any:
        """Count asyncio.run calls.

        Arguments:
            main: awaitable to run
            **kwargs: asyncio.run keyword arguments
        Returns:
            asyncio.run result
        """
        nonlocal run_count
        run_count += 1
        return real_asyncio_run(main, **kwargs)

    monkeypatch.setattr(
        "scinoephile.image.ocr.lens.lens_recognizer.asyncio.run",
        counting_run,
    )
    recognizer = CountingLensRecognizer(
        results=[
            ["Request error (possibly proxy-related): 502 Bad Gateway"],
            ["Request error (possibly proxy-related): 502 Bad Gateway"],
            ["recognized"],
        ],
    )
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "recognized"

    assert run_count == 1
    assert recognizer.predict_count == 3


def test_lens_recognizer_waits_between_transient_retries(monkeypatch: MonkeyPatch):
    """Test Google Lens waits before retrying transient failures.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    delays = patch_google_lens_sleep(monkeypatch)
    recognizer = CountingLensRecognizer(
        results=[
            ["Request error (possibly proxy-related): 502 Bad Gateway"],
            ["Request error (possibly proxy-related): 502 Bad Gateway"],
            ["recognized"],
        ],
    )
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "recognized"

    assert delays == [1.5, 1.5]


def test_lens_recognizer_retries_lens_api_errors(monkeypatch: MonkeyPatch):
    """Test Google Lens retries transient chrome-lens-py API errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    patch_google_lens_sleep(monkeypatch)
    recognizer = CountingLensRecognizer(
        exceptions=[
            FakeLensApiError("502 Bad Gateway"),
            FakeLensApiError("502 Bad Gateway"),
            None,
        ],
        results=[["recognized"]],
    )
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    assert recognizer.recognize_image(image) == "recognized"

    assert recognizer.predict_count == 3


def test_lens_recognizer_does_not_retry_nontransient_errors():
    """Test Google Lens does not retry deterministic API errors."""
    recognizer = CountingLensRecognizer(
        exceptions=[ValueError("deterministic failure")],
    )
    image = Image.new("RGBA", (10, 8), (255, 255, 255, 0))

    with raises(ValueError, match="deterministic failure"):
        recognizer.recognize_image(image)

    assert recognizer.predict_count == 1


def test_lens_recognizer_rejects_uncached_calls_in_async_loop(tmp_path: Path):
    """Test uncached synchronous recognition fails clearly in an async loop.

    Arguments:
        tmp_path: temporary path fixture
    """
    recognizer = CountingLensRecognizer(cache_dir_path=tmp_path)

    async def recognize() -> None:
        """Run synchronous recognition from an async context."""
        with raises(RuntimeError, match="cannot run uncached Google Lens OCR"):
            recognizer.recognize_image(Image.new("RGBA", (10, 8), (255, 255, 255, 0)))

    asyncio.run(recognize())


def test_lens_recognizer_import_error_is_actionable(monkeypatch: MonkeyPatch):
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

    with raises(ImportError, match="'ocr' extra"):
        LensRecognizer._import_chrome_lens_py_lens_api()


def test_lens_recognizer_imports_chrome_lens_py_only_when_needed():
    """Test importing Google Lens OCR does not import chrome-lens-py."""
    exitcode, _, _ = run_command(
        [
            sys.executable,
            "-c",
            (
                "import sys;"
                "import scinoephile.image.ocr.lens.lens_recognizer;"
                "raise SystemExit('chrome_lens_py' in sys.modules)"
            ),
        ],
    )

    assert exitcode == 0


def test_lens_recognizer_reuses_lens_api_client_per_instance(monkeypatch: MonkeyPatch):
    """Test each Google Lens recognizer reuses one LensAPI client.

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
    setattr(chrome_lens_py, "LensAPIError", FakeLensApiError)
    monkeypatch.setitem(sys.modules, "chrome_lens_py", chrome_lens_py)
    recognizer = LensRecognizer()

    assert recognizer.language is Language.eng
    assert recognizer.lens_language_code == "en"
    assert recognizer.retries == 3
    assert recognizer.recognize_image(Image.new("RGBA", (10, 8))) == "recognized"
    assert recognizer.recognize_image(Image.new("RGBA", (12, 9))) == "recognized"

    assert init_count == 1
