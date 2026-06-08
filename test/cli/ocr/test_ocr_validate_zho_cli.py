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

    validate_calls: list[tuple[Path, str, Path, bool]] = []

    def fake_validate_ocr(
        path: Path,
        language: str,
        *,
        cache_dir_path: Path,
        dev: bool = False,
    ) -> ImageSeries:
        """Fake OCR validation workflow."""
        validate_calls.append((path, language, cache_dir_path, dev))
        return tiny_image_series

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )

    outfile_path = tmp_path / "validated.srt"
    cache_dir_path = tmp_path / "cache"
    run_cli_with_args(
        OcrValidateCli,
        f"--language zho --infile {infile_path} --outfile {outfile_path} "
        f"--cache-dir {cache_dir_path}",
    )

    assert validate_calls == [(infile_path, "zho", cache_dir_path.resolve(), False)]
    output = outfile_path.read_text(encoding="utf-8")
    assert "recognized" in output
    assert "validated" in output


def test_ocr_validate_zho_cli_dev(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    tiny_image_series: ImageSeries,
):
    """Test OCR validate CLI forwards dev mode for Chinese subtitles.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
        tiny_image_series: small image subtitle series
    """
    validate_calls: list[tuple[Path, str, Path, bool]] = []

    def fake_validate_ocr(
        path: Path,
        language: str,
        *,
        cache_dir_path: Path,
        dev: bool = False,
    ) -> ImageSeries:
        """Fake OCR validation workflow."""
        validate_calls.append((path, language, cache_dir_path, dev))
        return tiny_image_series

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_ocr",
        fake_validate_ocr,
    )
    full_input_path = tmp_path / "image"
    full_input_path.mkdir()
    outfile_path = Path(tmp_path) / "validated.srt"
    cache_dir_path = tmp_path / "cache"

    run_cli_with_args(
        OcrValidateCli,
        f"--language zho --infile {full_input_path} --outfile {outfile_path} "
        f"--cache-dir {cache_dir_path} --dev",
    )

    assert validate_calls == [(full_input_path, "zho", cache_dir_path.resolve(), True)]


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
    run_calls: list[tuple[Path, Path, Path, str, int, bool]] = []

    def fake_run_ocr_validation_web(
        path: Path,
        outfile_path: Path,
        cache_dir_path: Path,
        *,
        host: str,
        port: int,
        dev: bool,
    ):
        """Capture web validation workflow arguments."""
        run_calls.append((path, outfile_path, cache_dir_path, host, port, dev))

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.run_ocr_validation_web",
        fake_run_ocr_validation_web,
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
        (infile_path, outfile_path, cache_dir_path.resolve(), "0.0.0.0", 5050, True)
    ]
