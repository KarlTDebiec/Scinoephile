#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli Yue review CLIs."""

from __future__ import annotations

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


def test_yue_review_nested_invocation_through_scinoephile():
    """Test `scinoephile yue review` runs through parent parser."""
    full_yuewen_input_path = (
        test_data_root / "kob/output/yue-Hans_timewarp_clean_flatten.srt"
    )
    full_zhongwen_input_path = test_data_root / "kob/output/zho-Hant_fuse.srt"

    expected = Series.load(full_yuewen_input_path)
    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.yue.yue_review_cli.get_yue_reviewed_vs_zho",
            return_value=expected,
        ) as patched_review:
            run_cli_with_args(
                ScinoephileCli,
                " ".join(
                    [
                        "yue review",
                        f"--yuewen-infile {full_yuewen_input_path}",
                        f"--zhongwen-infile {full_zhongwen_input_path}",
                        f"--outfile {output_path}",
                    ]
                ),
            )
        output = Series.load(output_path)

    assert patched_review.call_count == 1
    assert output == expected
