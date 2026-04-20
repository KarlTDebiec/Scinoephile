#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli Yue translation-vs-zho CLIs."""

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
    """Test 粤文 translation-vs-zho CLI help output.

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
    """Test 粤文 translation-vs-zho CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_yue_translate_vs_zho_cli_writes_file():
    """Test 粤文 translation-vs-zho CLI writes file output."""
    yue_infile_path = test_data_root / "mlamd" / "output" / "yue-Hans_transcribe.srt"
    zho_infile_path = test_data_root / "mlamd" / "output" / "zho-Hans_fuse.srt"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_translate_vs_zho_cli.get_yue_translated_vs_zho",
            return_value=expected_series,
        ) as patched_translate:
            run_cli_with_args(
                YueTranslateVsZhoCli,
                f"--yue-infile {yue_infile_path} "
                f"--zho-infile {zho_infile_path} "
                f"--outfile {outfile_path}",
            )
        output_series = Series.load(outfile_path)

    called_kwargs = patched_translate.call_args.kwargs
    assert called_kwargs["yuewen"] == Series.load(yue_infile_path)
    assert called_kwargs["zhongwen"] == Series.load(zho_infile_path)
    assert output_series == expected_series


def test_yue_translate_vs_zho_cli_rejects_two_stdin_infiles():
    """Test 粤文 translation-vs-zho CLI rejects stdin for both inputs."""
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranslateVsZhoCli,
            "--yue-infile - --zho-infile -",
        )


def test_yue_translate_vs_zho_cli_rejects_overwrite_without_outfile():
    """Test 粤文 translation-vs-zho CLI rejects overwrite when writing to stdout."""
    yue_infile_path = test_data_root / "mlamd" / "output" / "yue-Hans_transcribe.srt"
    zho_infile_path = test_data_root / "mlamd" / "output" / "zho-Hans_fuse.srt"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueTranslateVsZhoCli,
            f"--yue-infile {yue_infile_path} "
            f"--zho-infile {zho_infile_path} --overwrite",
        )
