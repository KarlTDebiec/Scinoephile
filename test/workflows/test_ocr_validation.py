#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries
from scinoephile.workflows.ocr_validation import validate_ocr


def _series_with_texts(texts: list[str]) -> Series:
    """Build a text series with one subtitle per provided text.

    Arguments:
        texts: subtitle texts
    Returns:
        text subtitle series
    """
    return Series(
        events=[
            Subtitle(start=(idx * 2000) + 1000, end=(idx * 2000) + 2000, text=text)
            for idx, text in enumerate(texts)
        ]
    )


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
    validate_calls: list[tuple[ImageSeries, int | None, bool, object]] = []

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

        def validate(
            self,
            series: ImageSeries,
            stop_at_idx: int | None = None,
            interactive: bool = True,
        ) -> Series:
            """Validate an image series."""
            validate_calls.append((series, stop_at_idx, interactive, self))
            return _series_with_texts(["validated"])

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
    )

    assert load_calls == [infile_path]
    assert manager_calls == [(cache_dir_path, True)]
    assert validate_calls == [(tiny_image_series, None, False, manager_instances[0])]
    assert [subtitle.text for subtitle in validated] == ["validated"]
    assert "validated" in outfile_path.read_text(encoding="utf-8")


def test_validate_ocr_ignores_interactive_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test interactive compatibility mode remains noninteractive."""
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"
    validate_calls: list[bool] = []

    class FakeValidationManager:
        """Fake validation manager."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | str | None = None,
            dev: bool = False,
        ):
            """Initialize."""

        def validate(
            self,
            series: ImageSeries,
            stop_at_idx: int | None = None,
            interactive: bool = True,
        ) -> Series:
            """Validate an image series."""
            validate_calls.append(interactive)
            return _series_with_texts(["validated"])

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        lambda path: tiny_image_series,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )

    validate_ocr(infile_path, outfile_path, interactive=True)

    assert validate_calls == [False]
