#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared LLM CLI provider arguments."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os import environ
from unittest.mock import patch

from pytest import mark, raises

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
from scinoephile.common.testing import run_cli_with_args


@mark.parametrize(
    "cli",
    [
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
    ],
)
def test_list_llm_providers(cli: type[CommandLineInterface]):
    """Test CLIs with LLM options can list available providers.

    Arguments:
        cli: CLI class under test
    """
    stdout = StringIO()
    stderr = StringIO()

    with raises(SystemExit, match="0"):
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli, "--list-llm-providers")

    listing = stdout.getvalue()
    assert stderr.getvalue() == ""
    assert listing.startswith("Available LLM providers:\n")
    assert "  deepseek  DeepSeek LLM Provider (OpenAI-SDK compatible)." in listing
    assert "default model: deepseek-v4-flash" in listing
    assert "API key env: DEEPSEEK_API_KEY" in listing
    assert "  openai    OpenAI LLM Provider." in listing
    assert "default model: gpt-5.4-mini" in listing
    assert "API key env: OPENAI_API_KEY" in listing


def test_list_llm_providers_uses_simplified_chinese_descriptions():
    """Test LLM provider listing localizes descriptions for zh-hans."""
    stdout = StringIO()
    stderr = StringIO()

    with patch.dict(environ, {"LC_ALL": "zh-hans"}, clear=False):
        with raises(SystemExit, match="0"):
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    run_cli_with_args(ZhoProcessCli, "--list-llm-providers")

    listing = stdout.getvalue()
    assert stderr.getvalue() == ""
    assert listing.startswith("可用 LLM 提供商：\n")
    assert "  deepseek  DeepSeek LLM 提供商（兼容 OpenAI SDK）。" in listing
    assert "default model: deepseek-v4-flash" in listing
    assert "API key env: DEEPSEEK_API_KEY" in listing
    assert "  openai    OpenAI LLM 提供商。" in listing
    assert "default model: gpt-5.4-mini" in listing
    assert "API key env: OPENAI_API_KEY" in listing


def test_llm_provider_arg_rejects_unknown_provider():
    """Test LLM provider argument rejects unknown provider names."""
    with raises(SystemExit, match="2"):
        run_cli_with_args(ZhoProcessCli, "--llm-provider missing-provider")
