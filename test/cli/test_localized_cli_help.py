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
        ("en", "dictionary search", "Search dictionaries"),
        ("zh-hans", "dictionary search", "查询词典"),
        ("zh-hant", "dictionary search", "查詢詞典"),
        ("en", "yue process", "Modify Written Cantonese subtitles"),
        ("zh-hans", "yue process", "修改书面粤语字幕"),
        ("zh-hant", "yue process", "修改書面粵語字幕"),
        ("en", "zho process", "Modify Standard Chinese subtitles"),
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


def test_locale_precedence_prefers_lc_all():
    """Test LC_ALL locale takes precedence over LANG."""
    with patch.dict(environ, {"LC_ALL": "en_US.UTF-8", "LANG": "zh_TW.UTF-8"}):
        output = _run_help("--help")
    assert "Command-line interface for Scinoephile" in output
