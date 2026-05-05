#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of OCR command-line interfaces."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

import pytest

from scinoephile.cli.ocr import OcrCli, OcrPaddleCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series, Subtitle
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (OcrCli,),
        (OcrCli, OcrPaddleCli),
        (ScinoephileCli, OcrCli, OcrPaddleCli),
    ],
)
def test_ocr_cli_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test OCR CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (OcrCli,),
        (OcrCli, OcrPaddleCli),
        (ScinoephileCli, OcrCli, OcrPaddleCli),
    ],
)
def test_ocr_cli_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test OCR CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_ocr_paddle_cli_help_lists_language_codes():
    """Test PaddleOCR CLI help lists common subtitle language codes."""
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(OcrPaddleCli, "-h")

    assert excinfo.value.code == 0
    assert stderr.getvalue() == ""
    help_text = " ".join(stdout.getvalue().split())
    assert "en (English)" in help_text
    assert "ch (simplified Chinese and English)" in help_text
    assert "chinese_cht (traditional Chinese)" in help_text


def test_ocr_paddle_cli_converts_image_subtitles_to_srt(
    monkeypatch: pytest.MonkeyPatch,
):
    """Test PaddleOCR CLI writes OCR output to SRT.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
    input_path = test_data_root / "mlamd/input/eng_ocr/source.sup"

    def fake_ocr_image_series_with_paddle(*args: object, **kwargs: object) -> Series:
        """Fake PaddleOCR image series processing.

        Arguments:
            *args: positional arguments
            **kwargs: keyword arguments
        Returns:
            text subtitle series
        """
        return Series(events=[Subtitle(start=1000, end=2000, text="recognized")])

    monkeypatch.setattr(
        "scinoephile.cli.ocr.ocr_paddle_cli.ocr_image_series_with_paddle",
        fake_ocr_image_series_with_paddle,
    )

    with get_temp_directory_path() as output_dir_path:
        output_path = output_dir_path / "ocr.srt"
        run_cli_with_args(
            OcrPaddleCli,
            f"--infile {input_path} --outfile {output_path}",
        )

        output = Series.load(output_path)
        assert [(event.start, event.end, event.text) for event in output] == [
            (1000, 2000, "recognized")
        ]
