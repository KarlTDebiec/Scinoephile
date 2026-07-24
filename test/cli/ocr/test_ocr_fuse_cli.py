#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ocr.OcrFuseCli."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch

from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import assert_series_equal, parametrize, test_data_root


def test_ocr_fuse_cli_uses_concise_json_help():
    """Test OCR-fusion JSON help describes its test-case contents."""
    actions = {
        action.dest: action
        for action in OcrFuseCli.argparser()._actions  # noqa: SLF001
    }

    assert actions["json_path"].help == "JSON file containing test cases"


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


def test_ocr_fuse_cli_passes_test_case_path(tmp_path: Path):
    """Test OCR-fusion CLI passes an optional test-case JSON path.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    lens_path = tmp_path / "lens.srt"
    tesseract_path = tmp_path / "tesseract.srt"
    json_path = tmp_path / "ocr_fusion.json"
    output_path = tmp_path / "fuse.srt"
    lens_path.write_text("1\n00:00:00,000 --> 00:00:00,500\nLens\n", encoding="utf-8")
    tesseract_path.write_text(
        "1\n00:00:00,000 --> 00:00:00,500\nTesseract\n",
        encoding="utf-8",
    )
    fused = Series(events=[Subtitle(start=0, end=500, text="Fused")])

    with patch(
        "scinoephile.cli.ocr.ocr_fuse_cli.fuse_ocr_series",
        return_value=fused,
    ) as fuse:
        run_cli_with_args(
            OcrFuseCli,
            f"--lens-infile {lens_path} --tesseract-infile {tesseract_path} "
            f"--language eng --json {json_path} --outfile {output_path}",
        )

    assert fuse.call_args.kwargs["test_case_path"] == json_path.resolve()
