#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CLI choice-like argument display."""

from __future__ import annotations

from argparse import Action

import pytest

from scinoephile.cli.multi.multi_stack_cli import MultiStackCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.ocr.ocr_lens_cli import OcrLensCli
from scinoephile.cli.ocr.ocr_paddle_cli import OcrPaddleCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.cli.ocr.ocr_tesseract_cli import OcrTesseractCli
from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.cli.yue.yue_translate_from_eng_cli import YueTranslateFromEngCli
from scinoephile.cli.yue.yue_translate_from_zho_cli import YueTranslateFromZhoCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.cli.zho.zho_translate_from_eng_cli import ZhoTranslateFromEngCli
from scinoephile.cli.zho.zho_translate_from_yue_cli import ZhoTranslateFromYueCli
from scinoephile.common import CommandLineInterface


@pytest.mark.parametrize(
    ("cli", "option", "metavar"),
    [
        (OcrFuseCli, "--language", "{eng,zho}"),
        (OcrLensCli, "--language", "{eng,zho-Hans,zho-Hant}"),
        (OcrPaddleCli, "--language", "{eng,zho-Hans,zho-Hant}"),
        (OcrProcessCli, "--language", "{eng,zho-Hans,zho-Hant}"),
        (OcrTesseractCli, "--language", "{eng,zho-Hans,zho-Hant}"),
        (OcrValidateCli, "--language", "{eng,zho}"),
        (MultiStackCli, "--sync", "{anchor-top,anchor-bottom,off}"),
        (YueProcessCli, "--proofread", "{simplified,traditional}"),
        (YueReviewVsZhoCli, "--mode", "{block,line}"),
        (YueReviewVsZhoCli, "--script", "{simplified,traditional}"),
        (YueTranscribeVsZhoCli, "--demucs", "{on,off}"),
        (YueTranscribeVsZhoCli, "--vad", "{auto,on,off}"),
        (YueTranscribeVsZhoCli, "--script", "{simplified,traditional}"),
        (YueTranslateFromEngCli, "--script", "{simplified,traditional}"),
        (YueTranslateFromZhoCli, "--script", "{simplified,traditional}"),
        (ZhoProcessCli, "--proofread", "{simplified,traditional}"),
        (ZhoTranslateFromEngCli, "--script", "{simplified,traditional}"),
        (ZhoTranslateFromYueCli, "--script", "{simplified,traditional}"),
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
