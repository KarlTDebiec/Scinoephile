#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation workflow helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.image.subtitles import ImageSeries
from scinoephile.workflows.ocr_validation import (
    run_ocr_validation_web,
    validate_ocr,
)


def test_validate_ocr_passes_eng_arguments_to_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR validation workflow passes English validation arguments.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    manager_instances: list[object] = []
    manager_calls: list[tuple[Path | str | None, bool]] = []
    validate_calls: list[tuple[ImageSeries, object]] = []

    class FakeValidationManager:
        """Fake validation manager."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | str | None = None,
            dev: bool = False,
        ):
            """Initialize."""
            manager_instances.append(self)
            manager_calls.append((cache_dir_path, dev))

    def fake_validate_eng_ocr(
        series: ImageSeries,
        validation_manager: object,
    ) -> ImageSeries:
        """Fake English OCR validation."""
        validate_calls.append((series, validation_manager))
        return series

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        lambda path: tiny_image_series,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.validate_eng_ocr",
        fake_validate_eng_ocr,
    )

    output = validate_ocr(
        tmp_path / "image",
        "eng",
        cache_dir_path=tmp_path / "cache",
        dev=True,
    )

    assert output is tiny_image_series
    assert manager_calls == [(tmp_path / "cache", True)]
    assert validate_calls == [(tiny_image_series, manager_instances[0])]


def test_validate_ocr_wraps_image_load_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validation workflow wraps image loading errors.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading failure."""
        raise ValueError(f"{path} is not an OCR image series")

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        fake_load,
    )

    with pytest.raises(ScinoephileError, match="not an OCR image series") as excinfo:
        validate_ocr(tmp_path / "image", "eng", cache_dir_path=tmp_path / "cache")

    assert isinstance(excinfo.value.__cause__, ValueError)


def test_run_ocr_validation_web_passes_arguments_to_web_app(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validation workflow passes web validation arguments.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    dir_path = tmp_path / "image"
    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    session = object()
    calls: list[tuple[object, ...]] = []

    def fake_from_dir_path(
        path: Path,
        *,
        outfile_path: Path | None = None,
        cache_dir_path: Path | None = None,
        dev: bool = False,
    ) -> object:
        """Fake web session construction."""
        calls.append(("from_dir_path", path, outfile_path, cache_dir_path, dev))
        return session

    class FakeFlaskApp:
        """Fake OCR validation Flask app."""

        def run(self, host: str, port: int):
            """Fake Flask app run."""
            calls.append(("run", host, port))

    def fake_create_app(value: object) -> FakeFlaskApp:
        """Fake Flask app creation."""
        calls.append(("create_app", value))
        return FakeFlaskApp()

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.OcrValidationSession.from_dir_path",
        fake_from_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.create_app",
        fake_create_app,
    )

    run_ocr_validation_web(
        dir_path,
        outfile_path,
        cache_dir_path,
        host="0.0.0.0",
        port=5050,
        dev=True,
    )

    assert calls == [
        ("from_dir_path", dir_path, outfile_path, cache_dir_path, True),
        ("create_app", session),
        ("run", "0.0.0.0", 5050),
    ]
