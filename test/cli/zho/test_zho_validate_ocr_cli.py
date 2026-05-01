#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoValidateOcrCli."""

from __future__ import annotations

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.zho.zho_cli import ZhoCli
from scinoephile.cli.zho.zho_validate_ocr_cli import ZhoValidateOcrCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.testing import run_cli_with_args
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


@pytest.mark.parametrize(
    ("input_path",),
    [
        ("mlamd/output/zho-Hans_image",),
        ("mlamd/input/zho-Hans_ocr/source.sup",),
    ],
)
def test_zho_validate_ocr_cli(input_path: str):
    """Test 中文 validate-ocr CLI processing with directory output.

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
            ZhoValidateOcrCli,
            f"--infile {full_input_path} --stop-at-idx 1 --outfile {outfile_path}",
        )

        output = ImageSeries.load(outfile_path)
        assert output == expected
        assert (outfile_path / "index.html").exists()
        assert any(outfile_path.glob("*.png"))
