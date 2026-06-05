#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CLI argument group assignments."""

from __future__ import annotations

from argparse import Action, ArgumentParser

import pytest

from scinoephile.cli.eng.eng_process_cli import EngProcessCli
from scinoephile.cli.eng.eng_translate_from_yue_cli import EngTranslateFromYueCli
from scinoephile.cli.eng.eng_translate_from_zho_cli import EngTranslateFromZhoCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.cli.yue.yue_translate_from_eng_cli import YueTranslateFromEngCli
from scinoephile.cli.yue.yue_translate_from_zho_cli import YueTranslateFromZhoCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.cli.zho.zho_translate_from_eng_cli import ZhoTranslateFromEngCli
from scinoephile.cli.zho.zho_translate_from_yue_cli import ZhoTranslateFromYueCli
from scinoephile.common import CommandLineInterface

LLM_CLIS: tuple[type[CommandLineInterface], ...] = (
    EngProcessCli,
    EngTranslateFromYueCli,
    EngTranslateFromZhoCli,
    OcrFuseCli,
    OcrProcessCli,
    YueProcessCli,
    YueReviewVsZhoCli,
    YueTranscribeVsZhoCli,
    YueTranslateFromEngCli,
    YueTranslateFromZhoCli,
    ZhoProcessCli,
    ZhoTranslateFromEngCli,
    ZhoTranslateFromYueCli,
)
"""CLI classes that expose shared LLM arguments."""


@pytest.mark.parametrize("cli", LLM_CLIS)
def test_llm_options_are_in_llm_argument_group(cli: type[CommandLineInterface]):
    """Test shared LLM options are grouped separately from operation options.

    Arguments:
        cli: CLI class to inspect
    """
    assert _get_action_group_title(cli, "--llm-provider") == "llm arguments"
    assert _get_action_group_title(cli, "--llm-model") == "llm arguments"
    assert (
        _get_action_group_title(cli, "--llm-additional-content-file") == "llm arguments"
    )
    assert _get_action_group_title(cli, "--list-llm-providers") == "additional help"


def _get_action(parser: ArgumentParser, option: str) -> Action:
    """Get a parser action by option string.

    Arguments:
        parser: parser to inspect
        option: option string to inspect
    Returns:
        matching argparse action
    Raises:
        AssertionError: if the option is not present
    """
    for action in parser._actions:  # noqa: SLF001
        if option in action.option_strings:
            return action
    raise AssertionError(f"{option} not found in {parser.prog}")


def _get_action_group_title(cli: type[CommandLineInterface], option: str) -> str:
    """Get the group title for a parser option.

    Arguments:
        cli: CLI class to inspect
        option: option string to inspect
    Returns:
        title of the argument group containing the option
    Raises:
        AssertionError: if the option is not assigned to a group
    """
    parser = cli.argparser()
    action = _get_action(parser, option)
    for group in parser._action_groups:  # noqa: SLF001
        if action in group._group_actions:  # noqa: SLF001
            if group.title is not None:
                return group.title
            break
    raise AssertionError(f"{option} is not assigned to an argument group")
