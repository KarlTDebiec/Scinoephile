#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_translate_vs_zho_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.yue.yue_cli import YueCli
from scinoephile.cli.yue.yue_translate_vs_zho_cli import YueTranslateVsZhoCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.translation import (
    YueVsZhoYueHansTranslationPrompt,
)
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueTranslateVsZhoCli,),
        (YueCli, YueTranslateVsZhoCli),
        (ScinoephileCli, YueCli, YueTranslateVsZhoCli),
    ],
)
def test_yue_translate_vs_zho_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test written Cantonese translate-vs-zho CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueTranslateVsZhoCli,),
        (YueCli, YueTranslateVsZhoCli),
        (ScinoephileCli, YueCli, YueTranslateVsZhoCli),
    ],
)
def test_yue_translate_vs_zho_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test written Cantonese translate-vs-zho CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("yue_input_path", "zho_input_path", "expected_path"),
    [
        (
            "mlamd/output/yue-Hans_transcribe/transcribe_review.srt",
            "mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt",
            "mlamd/output/yue-Hans_transcribe/transcribe_review_translate.srt",
        ),
    ],
)
def test_yue_translate_vs_zho_cli(
    yue_input_path: str,
    zho_input_path: str,
    expected_path: str,
):
    """Test written Cantonese translate-vs-zho CLI with file arguments.

    Arguments:
        yue_input_path: path to input written Cantonese subtitle fixture
        zho_input_path: path to input standard Chinese subtitle fixture
        expected_path: path to expected output subtitle fixture
    """
    full_yue_input_path = test_data_root / yue_input_path
    full_zho_input_path = test_data_root / zho_input_path
    full_expected_path = test_data_root / expected_path
    expected = Series.load(full_expected_path)

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_vs_zho_cli.get_yue_vs_zho_translator",
            return_value="translator",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_translate_vs_zho_cli.get_yue_translated_vs_zho",
                return_value=expected,
            ) as patched_translate:
                run_cli_with_args(
                    YueTranslateVsZhoCli,
                    f"--yue-infile {full_yue_input_path} "
                    f"--zho-infile {full_zho_input_path} "
                    f"--outfile {output_path}",
                )
        output = Series.load(output_path)

    assert (
        patched_factory.call_args.kwargs["prompt_cls"]
        is YueVsZhoYueHansTranslationPrompt
    )
    called_kwargs = patched_translate.call_args.kwargs
    assert called_kwargs["yuewen"] == Series.load(full_yue_input_path)
    assert called_kwargs["zhongwen"] == Series.load(full_zho_input_path)
    assert called_kwargs["translator"] == "translator"
    assert output == expected
