#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for localized CLI help output."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os import environ
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.testing import run_cli_with_args


def _run_help(args: str) -> str:
    """Run CLI help and return stdout text.

    Arguments:
        args: arguments to pass to root CLI
    Returns:
        help text written to stdout
    """
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(ScinoephileCli, args)
    assert excinfo.value.code == 0
    assert stderr.getvalue() == ""
    return stdout.getvalue()


@pytest.mark.parametrize(
    ("locale_name", "expected_fragments"),
    [
        ("en", ("Command-line interface for Scinoephile", "subcommand")),
        ("zh-hans", ("Scinoephile 命令行界面", "子命令", "选项")),
        ("zh-hant", ("Scinoephile 命令列介面", "子命令", "選項")),
    ],
)
def test_scinoephile_help_localized(
    locale_name: str, expected_fragments: tuple[str, ...]
):
    """Test root help output in each supported locale.

    Arguments:
        locale_name: CLI locale
        expected_fragments: phrases expected in help output
    """
    locale_env = {"LC_ALL": locale_name}
    with patch.dict(environ, locale_env):
        output = _run_help("--help")
    for fragment in expected_fragments:
        assert fragment in output


@pytest.mark.parametrize(
    ("locale_name", "subcommand", "expected_fragment"),
    [
        ("en", "analysis cer", "Calculate the Character Error Rate (CER)"),
        ("zh-hans", "analysis cer", "计算一个序列相对于另一个序列的字符错误率（CER）"),
        ("zh-hant", "analysis cer", "計算一個序列相對於另一個序列的字元錯誤率（CER）"),
        ("en", "analysis diff", "Calculate the diff between two series"),
        ("zh-hans", "analysis diff", "计算两个序列之间的差异"),
        ("zh-hant", "analysis diff", "計算兩個序列之間的差異"),
        ("en", "dictionary build", "Build dictionary caches"),
        ("zh-hans", "dictionary build", "构建词典缓存"),
        ("zh-hant", "dictionary build", "建立詞典快取"),
        ("en", "dictionary search", "Search dictionaries"),
        ("zh-hans", "dictionary search", "查询词典"),
        ("zh-hant", "dictionary search", "查詢詞典"),
        ("en", "eng fuse", "Fuse OCR output form Google Lens and Tesseract"),
        ("zh-hans", "eng fuse", "融合 Google Lens 与 Tesseract 的 OCR 输出"),
        ("zh-hant", "eng fuse", "融合 Google Lens 與 Tesseract 的 OCR 輸出"),
        ("en", "eng validate-ocr", "Validate OCR text against subtitle images"),
        ("zh-hans", "eng validate-ocr", "对照字幕图像校验 OCR 文本"),
        ("zh-hant", "eng validate-ocr", "對照字幕影像驗證 OCR 文字"),
        ("en", "yue process", "Modify written Cantonese subtitles"),
        ("zh-hans", "yue process", "修改书面粤语字幕"),
        ("zh-hant", "yue process", "修改書面粵語字幕"),
        ("en", "zho process", "Modify standard Chinese subtitles"),
        ("zh-hans", "zho process", "修改标准中文字幕"),
        ("zh-hant", "zho process", "修改標準中文字幕"),
    ],
)
def test_subcommand_help_localized(
    locale_name: str, subcommand: str, expected_fragment: str
):
    """Test representative subcommand help output in each locale.

    Arguments:
        locale_name: CLI locale
        subcommand: subcommand path
        expected_fragment: phrase expected in help output
    """
    locale_env = {"LC_ALL": locale_name}
    with patch.dict(environ, locale_env):
        output = _run_help(f"{subcommand} --help")
    assert expected_fragment in output


def test_locale_precedence_uses_environment_variable():
    """Test locale resolution falls back to environment variable."""
    with patch.dict(environ, {"LC_ALL": "zh-hant"}):
        output = _run_help("--help")
    assert "Scinoephile 命令列介面" in output


def test_locale_precedence_uses_encoded_environment_variable():
    """Test locale resolution handles locale encodings."""
    with patch.dict(environ, {"LC_ALL": "zh_CN.UTF-8"}):
        output = _run_help("--help")
    assert "Scinoephile 命令行界面" in output


def test_locale_precedence_prefers_lc_all():
    """Test LC_ALL locale takes precedence over LANG."""
    with patch.dict(environ, {"LC_ALL": "en_US.UTF-8", "LANG": "zh_TW.UTF-8"}):
        output = _run_help("--help")
    assert "Command-line interface for Scinoephile" in output


def test_locale_precedence_uses_encoded_lang():
    """Test locale resolution handles encoded LANG values."""
    with patch.dict(environ, {"LANG": "zh_TW.UTF-8"}, clear=True):
        output = _run_help("--help")
    assert "Scinoephile 命令列介面" in output
