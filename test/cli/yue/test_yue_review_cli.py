#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_review_cli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.yue.yue_cli import YueCli
from scinoephile.cli.yue.yue_review_cli import YueReviewCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueReviewCli,),
        (YueCli, YueReviewCli),
        (ScinoephileCli, YueCli, YueReviewCli),
    ],
)
def test_yue_review_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 review CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueReviewCli,),
        (YueCli, YueReviewCli),
        (ScinoephileCli, YueCli, YueReviewCli),
    ],
)
def test_yue_review_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 review CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_yue_review_help_describes_modes_and_stdin_behavior():
    """Test 粤文 review CLI help describes modes and stdin restrictions."""
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit, match="0"):
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(YueReviewCli, "-h")

    help_output = stdout.getvalue()
    assert "block-by-block review" in help_output
    assert "line-by-line proofreading" in help_output
    assert "may not both be '-'" in help_output
    assert stderr.getvalue() == ""


def test_yue_review_cli_defaults_to_block_mode():
    """Test 粤文 review CLI defaults to block mode."""
    yue_infile_path = test_data_root / "mlamd" / "output" / "yue-Hans_transcribe.srt"
    zho_infile_path = test_data_root / "mlamd" / "output" / "zho-Hans_fuse.srt"
    expected = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n默认块级审阅\n",
        format_="srt",
    )

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_review_cli.get_yue_reviewed_vs_zho",
            return_value=expected,
        ) as patched_review:
            with patch(
                "scinoephile.cli.yue.yue_review_cli.get_yue_proofread_vs_zho",
            ) as patched_line:
                run_cli_with_args(
                    YueReviewCli,
                    f"--yue-infile {yue_infile_path} "
                    f"--zho-infile {zho_infile_path} "
                    f"--outfile {outfile_path}",
                )
        output = Series.load(outfile_path)

    called_kwargs = patched_review.call_args.kwargs
    assert called_kwargs["yuewen"] == Series.load(yue_infile_path)
    assert called_kwargs["zhongwen"] == Series.load(zho_infile_path)
    patched_line.assert_not_called()
    assert output == expected


def test_yue_review_cli_line_mode():
    """Test 粤文 review CLI line mode dispatches proofreading."""
    yue_infile_path = test_data_root / "kob" / "output" / "yue-Hans_transcribe.srt"
    zho_infile_path = test_data_root / "kob" / "output" / "zho-Hant_fuse.srt"
    expected = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n逐行校对\n",
        format_="srt",
    )

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_review_cli.get_yue_proofread_vs_zho",
            return_value=expected,
        ) as patched_line:
            with patch(
                "scinoephile.cli.yue.yue_review_cli.get_yue_reviewed_vs_zho",
            ) as patched_review:
                run_cli_with_args(
                    YueReviewCli,
                    f"--yue-infile {yue_infile_path} "
                    f"--zho-infile {zho_infile_path} "
                    "--mode line "
                    f"--outfile {outfile_path}",
                )
        output = Series.load(outfile_path)

    called_kwargs = patched_line.call_args.kwargs
    assert called_kwargs["yuewen"] == Series.load(yue_infile_path)
    assert called_kwargs["zhongwen"] == Series.load(zho_infile_path)
    patched_review.assert_not_called()
    assert output == expected


def test_yue_review_cli_rejects_two_stdin_infiles():
    """Test 粤文 review CLI rejects stdin for both inputs."""
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueReviewCli,
            "--yue-infile - --zho-infile -",
        )


def test_yue_review_cli_rejects_overwrite_without_outfile():
    """Test 粤文 review CLI rejects overwrite when writing to stdout."""
    yue_infile_path = test_data_root / "mlamd" / "output" / "yue-Hans_transcribe.srt"
    zho_infile_path = test_data_root / "mlamd" / "output" / "zho-Hans_fuse.srt"

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            YueReviewCli,
            f"--yue-infile {yue_infile_path} "
            f"--zho-infile {zho_infile_path} "
            "--overwrite",
        )
