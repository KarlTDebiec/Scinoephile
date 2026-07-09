#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ocr.OcrFuseCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal, parametrize, test_data_root


@parametrize(
    ("lens_path", "secondary_path", "args", "expected_path"),
    [
        (
            "mnt/output/eng_ocr/lens.srt",
            "mnt/output/eng_ocr/tesseract.srt",
            "--language eng --tesseract-infile {secondary_path} --clean",
            "mnt/output/eng_ocr/fuse.srt",
        ),
        (
            "tmm/output/yue-Hans_ocr/lens.srt",
            "tmm/output/yue-Hans_ocr/paddle.srt",
            "--language yue-Hans --paddle-infile {secondary_path} --clean",
            "tmm/output/yue-Hans_ocr/fuse.srt",
        ),
        (
            "mnt/output/zho-Hans_ocr/lens.srt",
            "mnt/output/zho-Hans_ocr/paddle.srt",
            "--language zho-Hans --paddle-infile {secondary_path} --clean",
            "mnt/output/zho-Hans_ocr/fuse.srt",
        ),
    ],
)
def test_ocr_fuse_cli(
    lens_path: str,
    secondary_path: str,
    args: str,
    expected_path: str,
):
    """Test OCR fusion CLI with file arguments.

    Arguments:
        lens_path: path to Google Lens OCR subtitle fixture
        secondary_path: path to Tesseract or PaddleOCR subtitle fixture
        args: language and secondary-input CLI arguments
        expected_path: path to expected fused subtitle fixture
    """
    full_lens_path = test_data_root / lens_path
    full_secondary_path = test_data_root / secondary_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            OcrFuseCli,
            f"--lens-infile {full_lens_path} "
            f"{args.format(secondary_path=full_secondary_path)} "
            f"--outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


@parametrize(
    ("lens_path", "secondary_path", "args", "expected_path"),
    [
        (
            "mnt/output/eng_ocr/lens.srt",
            "mnt/output/eng_ocr/tesseract.srt",
            "--language eng --tesseract-infile {secondary_path} --clean",
            "mnt/output/eng_ocr/fuse.srt",
        ),
        (
            "mnt/output/zho-Hans_ocr/lens.srt",
            "mnt/output/zho-Hans_ocr/paddle.srt",
            "--language zho-Hans --paddle-infile {secondary_path} --clean",
            "mnt/output/zho-Hans_ocr/fuse.srt",
        ),
    ],
)
def test_ocr_fuse_cli_pipe(
    lens_path: str,
    secondary_path: str,
    args: str,
    expected_path: str,
):
    """Test OCR fusion CLI via stdin and stdout.

    Arguments:
        lens_path: path to Google Lens OCR subtitle fixture
        secondary_path: path to Tesseract or PaddleOCR subtitle fixture
        args: language and secondary-input CLI arguments
        expected_path: path to expected fused subtitle fixture
    """
    full_lens_path = test_data_root / lens_path
    full_secondary_path = test_data_root / secondary_path
    full_expected_path = test_data_root / expected_path
    stdin_stream = StringIO(full_lens_path.read_text(encoding="utf-8"))
    stdout_stream = StringIO()

    with patch("scinoephile.cli.helpers.io.stdin", stdin_stream):
        with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
            run_cli_with_args(
                OcrFuseCli,
                f"--lens-infile - {args.format(secondary_path=full_secondary_path)}",
            )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)
