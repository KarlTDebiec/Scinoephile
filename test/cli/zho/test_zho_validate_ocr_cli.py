#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoValidateOcrCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.zho.zho_cli import ZhoCli
from scinoephile.cli.zho.zho_validate_ocr_cli import ZhoValidateOcrCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho import validate_zho_ocr
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoValidateOcrCli,),
        (ZhoCli, ZhoValidateOcrCli),
        (ScinoephileCli, ZhoCli, ZhoValidateOcrCli),
    ],
)
def test_zho_validate_ocr_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 中文 validate-ocr CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoValidateOcrCli,),
        (ZhoCli, ZhoValidateOcrCli),
        (ScinoephileCli, ZhoCli, ZhoValidateOcrCli),
    ],
)
def test_zho_validate_ocr_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 中文 validate-ocr CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_zho_validate_ocr_help_documents_no_stdin():
    """Test 中文 validate-ocr help text documents stdin behavior."""
    stdout = StringIO()
    stderr = StringIO()

    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(ZhoValidateOcrCli, "-h")

    assert excinfo.value.code == 0
    assert "stdin is not supported" in stdout.getvalue()
    assert stderr.getvalue() == ""


def test_zho_validate_ocr_cli():
    """Test 中文 validate-ocr CLI processing with file output."""
    input_dir_path = test_data_root / "mlamd" / "output" / "zho-Hans_image"
    expected = validate_zho_ocr(
        ImageSeries.load(input_dir_path),
        stop_at_idx=1,
        interactive=False,
    )

    with get_temp_directory_path() as output_dir_path:
        with get_temp_file_path(".srt") as outfile_path:
            run_cli_with_args(
                ZhoValidateOcrCli,
                f"--infile {input_dir_path} "
                "--stop-at-idx 1 "
                f"--output-dir {output_dir_path} "
                f"--outfile {outfile_path}",
            )

            output = Series.load(outfile_path)
            assert output == expected
            assert any(output_dir_path.iterdir())


def test_zho_validate_ocr_cli_pipe():
    """Test 中文 validate-ocr CLI processing via stdout."""
    input_dir_path = test_data_root / "mlamd" / "output" / "zho-Hans_image"
    expected = validate_zho_ocr(
        ImageSeries.load(input_dir_path),
        stop_at_idx=0,
        interactive=False,
    )

    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdout", stdout_stream):
        run_cli_with_args(
            ZhoValidateOcrCli,
            f"--infile {input_dir_path} --stop-at-idx 0",
        )

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert output == expected


def test_zho_validate_ocr_cli_overwrite_without_outfile(capsys: pytest.CaptureFixture):
    """Test 中文 validate-ocr CLI rejects --overwrite without --outfile.

    Arguments:
        capsys: stdout/stderr capture fixture
    """
    input_dir_path = test_data_root / "mlamd" / "output" / "zho-Hans_image"

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            ZhoValidateOcrCli,
            f"--infile {input_dir_path} --overwrite",
        )

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert "--overwrite may only be used with --outfile" in captured.err


def test_zho_validate_ocr_cli_invalid_index(capsys: pytest.CaptureFixture):
    """Test 中文 validate-ocr CLI rejects an invalid stop index.

    Arguments:
        capsys: stdout/stderr capture fixture
    """
    input_dir_path = test_data_root / "mlamd" / "output" / "zho-Hans_image"

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            ZhoValidateOcrCli,
            f"--infile {input_dir_path} --stop-at-idx -1",
        )

    captured = capsys.readouterr()
    assert excinfo.value.code == 2
    assert "--stop-at-idx" in captured.err
