#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation workflow."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.workflows.ocr_validation import validate_ocr
from test.helpers.series_files import get_ocr_text_series


def test_validate_ocr_runs_noninteractive_validation(
    monkeypatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test path-based OCR validation loads, validates, and writes output."""
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    load_calls: list[Path] = []
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

        def validate(self, series: ImageSeries) -> Series:
            """Validate an image series."""
            validate_calls.append((series, self))
            return get_ocr_text_series("validated")

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading."""
        load_calls.append(path)
        return tiny_image_series

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        fake_load,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )

    validated = validate_ocr(
        infile_path,
        outfile_path,
        cache_dir_path=cache_dir_path,
        interactive=False,
        dev=True,
        overwrite=False,
        host="127.0.0.1",
        port=5000,
    )

    assert load_calls == [infile_path]
    assert manager_calls == [(cache_dir_path, True)]
    assert validate_calls == [(tiny_image_series, manager_instances[0])]
    assert [subtitle.text for subtitle in validated] == ["validated"]
    assert "validated" in outfile_path.read_text(encoding="utf-8")


def test_validate_ocr_runs_interactive_validation(
    monkeypatch,
    tmp_path: Path,
):
    """Test path-based OCR validation launches interactive validation."""
    infile_path = tmp_path / "image"
    infile_path.mkdir()
    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_calls = []
    session = object()

    def fake_session_from_dir_path(
        dir_path: Path,
        *,
        outfile_path: Path | None = None,
        cache_dir_path: Path | str | None = None,
        dev: bool = False,
    ) -> object:
        """Capture web session construction arguments."""
        run_calls.append(("from_dir_path", dir_path, outfile_path, cache_dir_path, dev))
        return session

    def fake_run_app(value: object, host: str, port: int):
        """Capture web app run arguments and write validation output."""
        run_calls.append(("run_app", value, host, port))
        get_ocr_text_series("interactive validated").save(outfile_path)

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.OcrValidationSession.from_dir_path",
        fake_session_from_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.run_app",
        fake_run_app,
    )

    validated = validate_ocr(
        infile_path,
        outfile_path,
        cache_dir_path=cache_dir_path,
        interactive=True,
        dev=True,
        overwrite=False,
        host="0.0.0.0",
        port=5050,
    )

    assert run_calls == [
        ("from_dir_path", infile_path, outfile_path, cache_dir_path, True),
        ("run_app", session, "0.0.0.0", 5050),
    ]
    assert [subtitle.text for subtitle in validated] == ["interactive validated"]
