#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR fuse CLI for standard Chinese subtitles."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from test.helpers import assert_series_equal


def _write_series(path: Path, text: str) -> Series:
    """Write a one-subtitle SRT fixture.

    Arguments:
        path: path to write
        text: subtitle text
    Returns:
        written subtitle series
    """
    source = f"1\n00:00:00,000 --> 00:00:01,000\n{text}\n"
    path.write_text(source, encoding="utf-8")
    return Series.from_string(source, format_="srt")


def test_ocr_fuse_zho_cli_writes_file_and_passes_conversion(tmp_path: Path):
    """Test standard Chinese OCR fuse CLI writes output with selected conversion."""
    lens_path = tmp_path / "lens.srt"
    paddle_path = tmp_path / "paddle.srt"
    output_path = tmp_path / "fused.srt"
    _write_series(lens_path, "鏡頭")
    _write_series(paddle_path, "桨")
    fused = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\nfused\n",
        format_="srt",
    )
    fuser = object()
    fuser_conversions: list[OpenCCConfig | None] = []

    def get_ocr_fuser(
        convert: OpenCCConfig | None,
        provider: object,
        additional_context: str | None,
    ) -> object:
        """Record fuser conversion config."""
        assert provider is not None
        assert additional_context is None
        fuser_conversions.append(convert)
        return fuser

    with (
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_provider",
        ),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_zho_cleaned",
            side_effect=lambda series, remove_empty: series,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_zho_converted",
            side_effect=lambda series, convert: series,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.OcrFuseCli._get_ocr_fuser",
            side_effect=get_ocr_fuser,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_zho_ocr_fused",
            return_value=fused,
        ),
    ):
        run_cli_with_args(
            OcrFuseCli,
            f"--language zho --lens-infile {lens_path} "
            f"--paddle-infile {paddle_path} --clean --convert t2s "
            f"--outfile {output_path}",
        )

    assert fuser_conversions == [OpenCCConfig.t2s]
    assert_series_equal(Series.load(output_path), fused)


def test_ocr_fuse_zho_cli_writes_stdout(tmp_path: Path):
    """Test standard Chinese OCR fuse CLI writes stdout when outfile is omitted."""
    lens_path = tmp_path / "lens.srt"
    paddle_path = tmp_path / "paddle.srt"
    _write_series(lens_path, "鏡頭")
    _write_series(paddle_path, "桨")
    fused = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n融合\n",
        format_="srt",
    )
    stdout_stream = StringIO()

    with (
        patch("scinoephile.cli.ocr.ocr_fuse_cli.get_provider"),
        patch("scinoephile.cli.ocr.ocr_fuse_cli.OcrFuseCli._get_ocr_fuser"),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_zho_ocr_fused",
            return_value=fused,
        ),
        patch("scinoephile.cli.helpers.io.stdout", stdout_stream),
    ):
        run_cli_with_args(
            OcrFuseCli,
            f"--language zho --lens-infile {lens_path} --paddle-infile {paddle_path}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output, fused)


def test_ocr_fuse_zho_cli_rejects_bare_convert_flag(tmp_path: Path):
    """Test OCR fuse CLI requires an explicit conversion config."""
    lens_path = tmp_path / "lens.srt"
    paddle_path = tmp_path / "paddle.srt"
    _write_series(lens_path, "鏡頭")
    _write_series(paddle_path, "桨")

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            OcrFuseCli,
            f"--language zho --lens-infile {lens_path} "
            f"--paddle-infile {paddle_path} --clean --convert",
        )
