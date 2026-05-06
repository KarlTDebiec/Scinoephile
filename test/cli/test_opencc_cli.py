#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of shared OpenCC CLI option listing."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from os import environ
from unittest.mock import patch

import pytest

from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.cli.zho.zho_fuse_cli import ZhoFuseCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args


@pytest.mark.parametrize(
    "cli",
    [
        ZhoProcessCli,
        ZhoFuseCli,
        YueProcessCli,
        YueTranscribeVsZhoCli,
    ],
)
def test_list_opencc_configs(cli: type[CommandLineInterface]):
    """Test CLIs with OpenCC options can list available configurations.

    Arguments:
        cli: CLI class under test
    """
    stdout = StringIO()
    stderr = StringIO()

    with pytest.raises(SystemExit, match="0"):
        with redirect_stdout(stdout):
            with redirect_stderr(stderr):
                run_cli_with_args(cli, "--list-opencc-configs")

    listing = stdout.getvalue()
    assert stderr.getvalue() == ""
    assert listing.startswith("Available OpenCC configurations:\n")
    assert "  hk2s  Traditional Chinese (Hong Kong) to Simplified Chinese.\n" in listing
    assert "  s2hk  Simplified Chinese to Traditional Chinese (Hong Kong).\n" in listing
    assert "  t2s   Traditional Chinese to Simplified Chinese.\n" in listing


def test_list_opencc_configs_uses_traditional_chinese_descriptions():
    """Test OpenCC configuration listing localizes descriptions for zh-hant."""
    stdout = StringIO()
    stderr = StringIO()

    with patch.dict(environ, {"LC_ALL": "zh-hant"}, clear=False):
        with pytest.raises(SystemExit, match="0"):
            with redirect_stdout(stdout):
                with redirect_stderr(stderr):
                    run_cli_with_args(ZhoProcessCli, "--list-opencc-configs")

    listing = stdout.getvalue()
    assert stderr.getvalue() == ""
    assert listing.startswith("可用 OpenCC 設定：\n")
    assert "  hk2s  繁體中文（香港標準）轉簡體中文。\n" in listing
    assert "  s2hk  簡體中文轉繁體中文（香港標準）。\n" in listing
    assert "  t2s   繁體中文轉簡體中文。\n" in listing
