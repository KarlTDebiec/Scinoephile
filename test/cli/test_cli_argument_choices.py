#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CLI choice-like argument display."""

from __future__ import annotations

from argparse import Action

import pytest

from scinoephile.cli.multi.multi_sync_cli import MultiSyncCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.cli.yue.yue_translate_vs_zho_cli import YueTranslateVsZhoCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.common import CommandLineInterface


@pytest.mark.parametrize(
    ("cli", "option", "metavar"),
    [
        (OcrFuseCli, "--language", "{eng,zho}"),
        (OcrValidateCli, "--language", "{eng,zho}"),
        (MultiSyncCli, "--timing", "{top,bottom,outer}"),
        (YueProcessCli, "--proofread", "{simplified,traditional}"),
        (YueReviewVsZhoCli, "--mode", "{block,line}"),
        (YueReviewVsZhoCli, "--script", "{simplified,traditional}"),
        (YueTranscribeVsZhoCli, "--demucs", "{on,off}"),
        (YueTranscribeVsZhoCli, "--vad", "{auto,on,off}"),
        (YueTranscribeVsZhoCli, "--script", "{simplified,traditional}"),
        (YueTranslateVsZhoCli, "--script", "{simplified,traditional}"),
        (ZhoProcessCli, "--proofread", "{simplified,traditional}"),
    ],
)
def test_custom_choice_validators_use_metavar_not_choices(
    cli: type[CommandLineInterface], option: str, metavar: str
):
    """Test custom validators are not duplicated with argparse choices.

    Arguments:
        cli: CLI class to inspect
        option: option string to inspect
        metavar: expected metavar for help display
    """
    action = _get_action(cli, option)

    assert action.choices is None
    assert action.metavar == metavar


def _get_action(cli: type[CommandLineInterface], option: str) -> Action:
    """Get a parser action by option string.

    Arguments:
        cli: CLI class to inspect
        option: option string to inspect
    Returns:
        matching argparse action
    Raises:
        AssertionError: if the option is not present
    """
    parser = cli.argparser()
    for action in parser._actions:  # noqa: SLF001
        if option in action.option_strings:
            return action
    raise AssertionError(f"{option} not found in {cli.__name__}")
