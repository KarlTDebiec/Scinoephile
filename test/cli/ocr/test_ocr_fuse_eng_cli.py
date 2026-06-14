#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the OCR fuse CLI for English subtitles."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal
from test.helpers.series_files import write_srt_series


def test_ocr_fuse_eng_cli_writes_file(tmp_path: Path):
    """Test English OCR fuse CLI writes fused output to a file."""
    lens_path = tmp_path / "lens.srt"
    tesseract_path = tmp_path / "tesseract.srt"
    output_path = tmp_path / "fused.srt"
    write_srt_series(lens_path, "lens")
    write_srt_series(tesseract_path, "tesseract")
    fused = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\nfused\n",
        format_="srt",
    )

    with (
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_provider",
        ),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_eng_cleaned",
            side_effect=lambda series, remove_empty: series,
        ),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_eng_ocr_fuser",
        ),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_eng_ocr_fused",
            return_value=fused,
        ),
    ):
        run_cli_with_args(
            OcrFuseCli,
            f"--language eng --lens-infile {lens_path} "
            f"--tesseract-infile {tesseract_path} --clean --outfile {output_path}",
        )

    assert_series_equal(Series.load(output_path), fused)


def test_ocr_fuse_eng_cli_writes_stdout(tmp_path: Path):
    """Test English OCR fuse CLI writes stdout when outfile is omitted."""
    lens_path = tmp_path / "lens.srt"
    tesseract_path = tmp_path / "tesseract.srt"
    write_srt_series(lens_path, "lens")
    write_srt_series(tesseract_path, "tesseract")
    fused = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\nfused\n",
        format_="srt",
    )
    stdout_stream = StringIO()

    with (
        patch("scinoephile.cli.ocr.ocr_fuse_cli.get_provider"),
        patch("scinoephile.cli.ocr.ocr_fuse_cli.get_eng_ocr_fuser"),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_eng_ocr_fused",
            return_value=fused,
        ),
        patch("scinoephile.cli.helpers.io.stdout", stdout_stream),
    ):
        run_cli_with_args(
            OcrFuseCli,
            f"--language eng --lens-infile {lens_path} "
            f"--tesseract-infile {tesseract_path}",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output, fused)


def test_ocr_fuse_eng_cli_overwrites_existing_file(tmp_path: Path):
    """Test English OCR fuse CLI overwrites existing output files."""
    lens_path = tmp_path / "lens.srt"
    tesseract_path = tmp_path / "tesseract.srt"
    output_path = tmp_path / "fused.srt"
    write_srt_series(lens_path, "lens")
    write_srt_series(tesseract_path, "tesseract")
    output_path.write_text("existing\n", encoding="utf-8")
    fused = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\nfused\n",
        format_="srt",
    )

    with (
        patch("scinoephile.cli.ocr.ocr_fuse_cli.get_provider"),
        patch("scinoephile.cli.ocr.ocr_fuse_cli.get_eng_ocr_fuser"),
        patch(
            "scinoephile.cli.ocr.ocr_fuse_cli.get_eng_ocr_fused",
            return_value=fused,
        ),
    ):
        run_cli_with_args(
            OcrFuseCli,
            f"--language eng --lens-infile {lens_path} "
            f"--tesseract-infile {tesseract_path} --outfile {output_path} "
            "--overwrite",
        )

    assert_series_equal(Series.load(output_path), fused)
