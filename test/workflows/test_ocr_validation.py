#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR validation workflow."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.image.subtitles import ImageSeries
from scinoephile.web.ocr_validation.html_index import load_html_entries
from scinoephile.workflows import ocr_validation
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


def test_ocr_validation_exports_public_workflow_api():
    """Test OCR validation exposes only its public workflow operation."""
    assert ocr_validation.__all__ == ["validate_ocr"]


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

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading."""
        load_calls.append(path)
        return tiny_image_series

    def fake_validate_eng_ocr(
        series: ImageSeries,
        validation_manager: object,
    ) -> Series:
        """Fake English OCR validation."""
        validate_calls.append((series, validation_manager))
        return _series_with_texts(["validated"])

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ImageSeries.load",
        fake_load,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.validate_eng_ocr",
        fake_validate_eng_ocr,
    )

    validated = validate_ocr(
        infile_path,
        "eng",
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


def test_validate_ocr_applies_text_series_to_image_dir(
    monkeypatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR validation can apply text to an image subtitle directory."""
    infile_path = tmp_path / "image"
    tiny_image_series.save(infile_path)
    outfile_path = tmp_path / "validated.srt"
    text_series = _series_with_texts(["fused 1", "fused 2"])
    manager_instances: list[object] = []
    validate_calls: list[tuple[list[str], object]] = []

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

    def fake_validate_eng_ocr(
        series: ImageSeries,
        validation_manager: object,
    ) -> Series:
        """Fake English OCR validation."""
        validate_calls.append(
            ([subtitle.text for subtitle in series], validation_manager)
        )
        return _series_with_texts(["validated 1", "validated 2"])

    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.ValidationManager",
        FakeValidationManager,
    )
    monkeypatch.setattr(
        "scinoephile.workflows.ocr_validation.validate_eng_ocr",
        fake_validate_eng_ocr,
    )

    validated = validate_ocr(
        infile_path,
        "eng",
        outfile_path,
        text_series=text_series,
    )

    assert validate_calls == [(["fused 1", "fused 2"], manager_instances[0])]
    assert [entry.text for entry in load_html_entries(infile_path)] == [
        "fused 1",
        "fused 2",
    ]
    assert [subtitle.text for subtitle in validated] == [
        "validated 1",
        "validated 2",
    ]


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
        _series_with_texts(["interactive validated"]).save(outfile_path)

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
        "zho",
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
