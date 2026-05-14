#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.EngValidateOcrCli."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.ocr.ocr_cli import OcrCli
from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_validation import validate_eng_ocr
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
def test_eng_validate_ocr_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test English validate-ocr CLI help output.

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
def test_eng_validate_ocr_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test English validate-ocr CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("input_path",),
    [
        ("mlamd/output/eng_ocr/image",),
        ("mlamd/input/eng_ocr/source.sup",),
    ],
)
def test_eng_validate_ocr_cli(input_path: str):
    """Test English validate-ocr CLI processing with directory output.

    Arguments:
        input_path: path to input image subtitle fixture
    """
    full_input_path = test_data_root / input_path
    expected = validate_eng_ocr(
        ImageSeries.load(full_input_path),
        stop_at_idx=1,
        interactive=False,
    )

    with get_temp_directory_path() as output_dir_path:
        outfile_path = output_dir_path / "validated"
        run_cli_with_args(
            OcrValidateCli,
            f"--language eng --infile {full_input_path} --stop-at-idx 1 "
            f"--outfile {outfile_path}",
        )

        output = ImageSeries.load(outfile_path)
        assert_series_equal(output, expected)
        assert (outfile_path / "index.html").exists()
        assert any(outfile_path.glob("*.png"))


def test_eng_validate_ocr_cli_dev(monkeypatch, tmp_path):
    """Test English validate-ocr CLI forwards dev mode.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tmp_path: pytest temporary path fixture
    """
    captured_dev = None

    def mock_validate_eng_ocr(
        series: ImageSeries,
        stop_at_idx: int | None = None,
        interactive: bool = False,
        dev: bool = False,
    ) -> ImageSeries:
        """Mock English OCR validation.

        Arguments:
            series: ImageSeries to validate
            stop_at_idx: stop processing at this index
            interactive: whether to prompt user for confirmations
            dev: whether to write validation data updates to the repo
        Returns:
            input image series
        """
        nonlocal captured_dev
        captured_dev = dev
        return series

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_validate_cli.validate_eng_ocr",
        mock_validate_eng_ocr,
    )
    full_input_path = test_data_root / "mlamd/output/eng_ocr/image"
    outfile_path = Path(tmp_path) / "validated"

    run_cli_with_args(
        OcrValidateCli,
        f"--language eng --infile {full_input_path} --outfile {outfile_path} --dev",
    )

    assert captured_dev is True
