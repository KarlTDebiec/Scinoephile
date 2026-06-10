#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries
from scinoephile.workflows.ocr_validation import validate_ocr


def test_validate_ocr_runs_validation(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test path-based OCR validation loads, validates, and writes output.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
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
            """Initialize.

            Arguments:
                cache_dir_path: cache directory for local OCR validation data
                dev: whether validation should write data updates to repo data
            """
            manager_instances.append(self)
            manager_calls.append((cache_dir_path, dev))

        def validate(self, series: ImageSeries) -> Series:
            """Validate an image series.

            Arguments:
                series: image series to validate
            Returns:
                validated text subtitle series
            """
            validate_calls.append((series, self))
            return _series_with_texts(["validated"])

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading.

        Arguments:
            path: image subtitle input path
        Returns:
            configured image subtitle series
        """
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
        dev=True,
    )

    assert load_calls == [infile_path]
    assert manager_calls == [(cache_dir_path, True)]
    assert validate_calls == [(tiny_image_series, manager_instances[0])]
    assert [subtitle.text for subtitle in validated] == ["validated"]
    assert "validated" in outfile_path.read_text(encoding="utf-8")


def test_validate_ocr_reuses_existing_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validation reuses an existing output without overwrite.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"
    _series_with_texts(["existing"]).save(outfile_path)

    def fail_load(path: Path) -> ImageSeries:
        """Fail if image subtitle loading is attempted."""
        raise AssertionError(f"unexpected load: {path}")

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        fail_load,
    )

    validated = validate_ocr(infile_path, outfile_path)

    assert [subtitle.text for subtitle in validated] == ["existing"]


def test_validate_ocr_overwrites_existing_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR validation overwrites an existing output when requested.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"
    _series_with_texts(["existing"]).save(outfile_path)

    class FakeValidationManager:
        """Fake validation manager."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | str | None = None,
            dev: bool = False,
        ):
            """Initialize."""
            _ = cache_dir_path, dev

        def validate(self, series: ImageSeries) -> Series:
            """Validate an image series."""
            _ = series
            return _series_with_texts(["overwritten"])

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        lambda path: tiny_image_series,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )

    validated = validate_ocr(infile_path, outfile_path, overwrite=True)

    assert [subtitle.text for subtitle in validated] == ["overwritten"]


def test_validate_ocr_wraps_validation_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR validation wraps lower-level validation failures.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    infile_path = tmp_path / "source.sup"
    infile_path.write_bytes(b"unused")
    outfile_path = tmp_path / "validated.srt"

    class FakeValidationManager:
        """Fake validation manager."""

        def __init__(
            self,
            *,
            cache_dir_path: Path | str | None = None,
            dev: bool = False,
        ):
            """Initialize."""
            _ = cache_dir_path, dev

        def validate(self, series: ImageSeries) -> Series:
            """Validate an image series."""
            _ = series
            raise ValueError("bad validation data")

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        lambda path: tiny_image_series,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )

    with pytest.raises(ScinoephileError, match="Unable to validate OCR") as excinfo:
        validate_ocr(infile_path, outfile_path)

    assert isinstance(excinfo.value.__cause__, ValueError)


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
