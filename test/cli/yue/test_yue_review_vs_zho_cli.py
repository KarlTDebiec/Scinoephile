#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_review_vs_zho_cli."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.yue.yue_cli import YueCli
from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.block_review import YueHansBlockReviewPrompt
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueReviewVsZhoCli,),
        (YueCli, YueReviewVsZhoCli),
        (ScinoephileCli, YueCli, YueReviewVsZhoCli),
    ],
)
def test_yue_review_vs_zho_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 review-vs-zho CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueReviewVsZhoCli,),
        (YueCli, YueReviewVsZhoCli),
        (ScinoephileCli, YueCli, YueReviewVsZhoCli),
    ],
)
def test_yue_review_vs_zho_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 review-vs-zho CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("yue_input_path", "zho_input_path", "expected_path", "args"),
    [
        (
            "mlamd/output/yue-Hans_transcribe.srt",
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/yue-Hans_transcribe_review.srt",
            "--mode line",
        ),
        (
            "mlamd/output/yue-Hans_transcribe_review_translate.srt",
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/yue-Hans_transcribe_review_translate_block_review.srt",
            "",
        ),
    ],
)
def test_yue_review_vs_zho_cli(
    yue_input_path: str,
    zho_input_path: str,
    expected_path: str,
    args: str,
):
    """Test 粤文 review-vs-zho CLI with file arguments."""
    full_yue_input_path = test_data_root / yue_input_path
    full_zho_input_path = test_data_root / zho_input_path
    full_expected_path = test_data_root / expected_path
    expected = Series.load(full_expected_path)

    with get_temp_file_path(".srt") as outfile_path:
        with patch(
            "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_vs_zho_block_reviewer",
            return_value="reviewer",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_block_reviewed_vs_zho",
                return_value=expected,
            ) as patched_review:
                with patch(
                    "scinoephile.cli.yue.yue_review_vs_zho_cli.get_yue_line_reviewed_vs_zho",
                    return_value=expected,
                ) as patched_line:
                    run_cli_with_args(
                        YueReviewVsZhoCli,
                        f"--yue-infile {full_yue_input_path} "
                        f"--zho-infile {full_zho_input_path} "
                        f"{args} "
                        f"--outfile {outfile_path}",
                    )
        output = Series.load(outfile_path)

    if args == "--mode line":
        called_kwargs = patched_line.call_args.kwargs
        assert called_kwargs["yuewen"] == Series.load(full_yue_input_path)
        assert called_kwargs["zhongwen"] == Series.load(full_zho_input_path)
        patched_review.assert_not_called()
        patched_factory.assert_not_called()
    else:
        assert (
            patched_factory.call_args.kwargs["prompt_cls"] is YueHansBlockReviewPrompt
        )
        called_kwargs = patched_review.call_args.kwargs
        assert called_kwargs["yuewen"] == Series.load(full_yue_input_path)
        assert called_kwargs["zhongwen"] == Series.load(full_zho_input_path)
        assert called_kwargs["reviewer"] == "reviewer"
        patched_line.assert_not_called()
    assert output == expected
