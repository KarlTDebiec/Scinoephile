#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ScinoephileCli."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os import environ
from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage


def test_scinoephile_help():
    """Test root CLI help output."""
    assert_cli_help((ScinoephileCli,))


def test_scinoephile_usage():
    """Test root CLI usage output."""
    assert_cli_usage((ScinoephileCli,))


def test_scinoephile_help_does_not_create_default_cache_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test root help output does not create default cache directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    cache_dir_path = tmp_path / "cache"
    monkeypatch.setenv("SCINOEPHILE_CACHE_DIR", str(cache_dir_path))

    assert_cli_help((ScinoephileCli,))

    assert not cache_dir_path.exists()


def test_scinoephile_all_commands_lists_complete_hierarchy():
    """Test root CLI can list the complete subcommand hierarchy."""
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(SystemExit) as excinfo:
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(ScinoephileCli, "--all-commands")

    output = stdout.getvalue()
    assert excinfo.value.code == 0
    assert stderr.getvalue() == ""
    assert output.startswith("Available subcommands:\n\n")
    assert "\nanalysis" in output
    assert "\n    cer" in output
    assert "\ndictionary" in output
    assert "\n    build" in output
    assert "\n        wiktionary" in output
    assert "\neng" in output
    assert "\n    validate-ocr" in output
    assert "\nzho" in output
    assert "\n    fuse" in output
    assert "\n    process" in output
    assert "\n    validate-ocr" in output
    assert all(len(line) <= 80 for line in output.splitlines())
    assert "    transcribe-vs-zho" in output
    assert "transcribe subtitles from audio and revise using" in output
    assert "standard Chinese text" in output
    assert "\n                        standard Chinese text" in output


def test_scinoephile_all_commands_localized():
    """Test all-commands output localizes command descriptions."""
    with patch.dict(environ, {"LC_ALL": "zh-hant"}):
        stdout = StringIO()
        stderr = StringIO()
        with pytest.raises(SystemExit) as excinfo:
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    run_cli_with_args(ScinoephileCli, "--all-commands")

    output = stdout.getvalue()
    assert excinfo.value.code == 0
    assert stderr.getvalue() == ""
    assert "可用子命令：" in output
    assert "子命令" in output
    assert "\nzho" in output
    assert "\n    process" in output
    assert "修改標準中文字幕" in output
    assert "香港中文大學現代標準漢語與粵語對照資料庫" not in output
    assert "由 2004 年第二版《廣州話正音字典》整理而成" not in output
