#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ProcessCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from scinoephile.cli.process_cli import ProcessCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal, parametrize, test_data_root


@parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "mnt/output/eng_ocr/fuse.srt",
            "--clean",
            "mnt/output/eng_ocr/fuse_clean.srt",
        ),
        (
            "mnt/output/zho-Hans_ocr/fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_ocr/fuse_clean.srt",
        ),
        (
            "mnt/output/zho-Hant_ocr/fuse_clean_validate_review_flatten.srt",
            "--convert t2s",
            "mnt/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify.srt",
        ),
        (
            "kob/output/yue-Hans/clean_review_flatten_timewarp.srt",
            "--romanize",
            "kob/output/yue-Hans/clean_review_flatten_timewarp_romanize.srt",
        ),
    ],
)
def test_process_cli(input_path: str, args: str, expected_path: str):
    """Test language-aware processing CLI with file arguments.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ProcessCli,
            f"--infile {full_input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


@parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "mnt/output/zho-Hans_ocr/fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_ocr/fuse_clean.srt",
        ),
    ],
)
def test_process_cli_pipe(input_path: str, args: str, expected_path: str):
    """Test processing CLI via stdin/stdout.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path
    input_text = full_input_path.read_text(encoding="utf-8")

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.cli.helpers.io.stdin", stdin_stream):
        with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
            run_cli_with_args(ProcessCli, f"--infile - {args}")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)
