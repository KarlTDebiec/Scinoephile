#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoValidateOcrCli."""

from __future__ import annotations

import pytest

from scinoephile.cli.ocr.ocr_cli import OcrCli
from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.ocr_validation import validate_zho_ocr
from test.helpers import (
    assert_cli_help,
    assert_cli_usage,
    assert_series_equal,
    test_data_root,
)


@pytest.mark.parametrize(
    "cli",
    [
        (OcrValidateCli,),
        (OcrCli, OcrValidateCli),
        (ScinoephileCli, OcrCli, OcrValidateCli),
    ],
)
def test_zho_validate_ocr_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese validate-ocr CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (OcrValidateCli,),
        (OcrCli, OcrValidateCli),
        (ScinoephileCli, OcrCli, OcrValidateCli),
    ],
)
def test_zho_validate_ocr_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese validate-ocr CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("input_path",),
    [
        ("mlamd/output/zho-Hans_ocr/image",),
        ("mlamd/input/zho-Hans_ocr/source.sup",),
    ],
)
def test_zho_validate_ocr_cli(input_path: str):
    """Test standard Chinese validate-ocr CLI processing with directory output.

    Arguments:
        input_path: path to input image subtitle fixture
    """
    full_input_path = test_data_root / input_path
    expected = validate_zho_ocr(
        ImageSeries.load(full_input_path),
        stop_at_idx=1,
        interactive=False,
    )

    with get_temp_directory_path() as output_dir_path:
        outfile_path = output_dir_path / "validated"
        run_cli_with_args(
            OcrValidateCli,
            f"--language zho --infile {full_input_path} --stop-at-idx 1 "
            f"--outfile {outfile_path}",
        )

        output = ImageSeries.load(outfile_path)
        assert_series_equal(output, expected)
        assert (outfile_path / "index.html").exists()
        assert any(outfile_path.glob("*.png"))
