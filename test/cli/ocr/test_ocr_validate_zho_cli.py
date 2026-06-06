#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR validate CLI for standard Chinese subtitles."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.image.subtitles import ImageSeries


@pytest.mark.parametrize(
    ("input_path",),
    [
        ("mlamd/output/zho-Hans_ocr/image",),
        ("mlamd/input/zho-Hans_ocr/source.sup",),
    ],
)
def test_ocr_validate_zho_cli(
    input_path: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR validate CLI processing for standard Chinese subtitles.

    Arguments:
        input_path: path to input image subtitle fixture
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    infile_path = tmp_path / input_path
    infile_path.parent.mkdir(parents=True, exist_ok=True)
    if infile_path.suffix:
        infile_path.write_bytes(b"unused")
    else:
        infile_path.mkdir()

    load_paths: list[Path] = []
    validate_calls: list[tuple[ImageSeries, Path, bool]] = []

    def fake_load(path: Path) -> ImageSeries:
        """Fake image subtitle loading.

        Arguments:
            path: image subtitle input path
        Returns:
            configured image subtitle series
        """
        load_paths.append(path)
        return tiny_image_series

    def fake_validate_zho_ocr(
        series: ImageSeries,
        *,
        cache_dir_path: Path,
        dev: bool = False,
    ) -> ImageSeries:
        """Fake standard Chinese OCR validation.

        Arguments:
            series: ImageSeries to validate
            cache_dir_path: cache directory path
            dev: whether to write validation data updates to the repo
        Returns:
            configured validated image series
        """
        validate_calls.append((series, cache_dir_path, dev))
        return tiny_image_series

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.ImageSeries.load",
        fake_load,
    )
    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_zho_ocr",
        fake_validate_zho_ocr,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language zho --infile {infile_path} --outfile {outfile_path} "
        f"--cache-dir {cache_dir_path}",
    )

    assert load_paths == [infile_path]
    assert validate_calls == [(tiny_image_series, cache_dir_path.resolve(), False)]
    output = outfile_path.read_text(encoding="utf-8")
    assert "recognized" in output
    assert "validated" in output


def test_ocr_validate_zho_cli_web(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """Test OCR validate CLI launches web validation for Chinese subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    infile_path = tmp_path / "image"
    infile_path.mkdir()
    (infile_path / "index.html").write_text("<html></html>", encoding="utf-8")
    run_calls = []
    session = object()

    def fake_session_from_dir_path(
        dir_path: Path,
        *,
        outfile_path: Path | None = None,
        cache_dir_path: Path | None = None,
        dev: bool = False,
    ) -> object:
        """Capture web session construction arguments."""
        run_calls.append(("from_dir_path", dir_path, outfile_path, cache_dir_path, dev))
        return session

    class FakeFlaskApp:
        """Fake OCR validation Flask app."""

        def run(
            self,
            *,
            host: str = "127.0.0.1",
            port: int = 5000,
        ):
            """Capture web app run arguments."""
            run_calls.append(("run", host, port))

    def fake_create_app(value: object) -> FakeFlaskApp:
        """Capture Flask app construction arguments."""
        run_calls.append(("create_app", value))
        return FakeFlaskApp()

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.OcrValidationSession.from_dir_path",
        fake_session_from_dir_path,
    )
    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.create_app",
        fake_create_app,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language zho --infile {infile_path} --dev "
        f"--interactive --host 0.0.0.0 --port 5050 "
        f"--cache-dir {cache_dir_path} --outfile {outfile_path}",
    )

    assert run_calls == [
        ("from_dir_path", infile_path, outfile_path, cache_dir_path.resolve(), True),
        ("create_app", session),
        ("run", "0.0.0.0", 5050),
    ]
