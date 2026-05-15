#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared LLM CLI provider arguments."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os import environ
from unittest.mock import patch

import pytest

from scinoephile.cli.eng.eng_process_cli import EngProcessCli
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.cli.yue.yue_translate_vs_zho_cli import YueTranslateVsZhoCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args


@pytest.mark.parametrize(
    "cli",
    [
        EngProcessCli,
        OcrFuseCli,
        YueProcessCli,
        YueReviewVsZhoCli,
        YueTranscribeVsZhoCli,
        YueTranslateVsZhoCli,
        ZhoProcessCli,
    ],
)
def test_list_llm_providers(cli: type[CommandLineInterface]):
    """Test CLIs with LLM options can list available providers.

    Arguments:
        cli: CLI class under test
    """
    stdout = StringIO()
    stderr = StringIO()

    with pytest.raises(SystemExit, match="0"):
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli, "--list-llm-providers")

    listing = stdout.getvalue()
    assert stderr.getvalue() == ""
    assert listing.startswith("Available LLM providers:\n")
    assert "  deepseek  DeepSeek LLM Provider (OpenAI-SDK compatible).\n" in listing
    assert "  openai    OpenAI LLM Provider.\n" in listing


def test_list_llm_providers_uses_simplified_chinese_descriptions():
    """Test LLM provider listing localizes descriptions for zh-hans."""
    stdout = StringIO()
    stderr = StringIO()

    with patch.dict(environ, {"LC_ALL": "zh-hans"}, clear=False):
        with pytest.raises(SystemExit, match="0"):
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    run_cli_with_args(ZhoProcessCli, "--list-llm-providers")

    listing = stdout.getvalue()
    assert stderr.getvalue() == ""
    assert listing.startswith("可用 LLM 提供商：\n")
    assert "  deepseek  DeepSeek LLM 提供商（兼容 OpenAI SDK）。\n" in listing
    assert "  openai    OpenAI LLM 提供商。\n" in listing


def test_llm_provider_arg_rejects_unknown_provider():
    """Test LLM provider argument rejects unknown provider names."""
    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(ZhoProcessCli, "--llm-provider missing-provider")
