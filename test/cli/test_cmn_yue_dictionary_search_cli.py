#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.CmnYueDictionarySearchCli."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import ExitStack
from pathlib import Path

import pytest

from scinoephile.cli import (
    CmnYueCli,
    CmnYueDictionaryCli,
    CmnYueDictionarySearchCli,
    ScinoephileCli,
)
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage, skip_if_ci


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueDictionarySearchCli,),
        (CmnYueDictionaryCli, CmnYueDictionarySearchCli),
        (CmnYueCli, CmnYueDictionaryCli, CmnYueDictionarySearchCli),
        (ScinoephileCli, CmnYueCli, CmnYueDictionaryCli, CmnYueDictionarySearchCli),
    ],
)
def test_cmn_yue_dictionary_search_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test CUHK dictionary search CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CmnYueDictionarySearchCli,),
        (CmnYueDictionaryCli, CmnYueDictionarySearchCli),
        (CmnYueCli, CmnYueDictionaryCli, CmnYueDictionarySearchCli),
        (ScinoephileCli, CmnYueCli, CmnYueDictionaryCli, CmnYueDictionarySearchCli),
    ],
)
def test_cmn_yue_dictionary_search_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test CUHK dictionary search CLI usage output."""
    assert_cli_usage(cli)


@pytest.fixture(scope="module")
def cuhk_database_path() -> Generator[Path]:
    """Build a temporary CUHK database for end-to-end search tests."""
    with ExitStack() as stack:
        cache_dir_path = stack.enter_context(get_temp_directory_path())
        database_path = stack.enter_context(get_temp_file_path(".db"))
        run_cli_with_args(
            ScinoephileCli,
            "cmn_yue dictionary build "
            f"--cache-dir {cache_dir_path} "
            f"--database-path {database_path} "
            "--max-words 10 "
            "--overwrite "
            "--min-delay-seconds 0 "
            "--max-delay-seconds 0 "
            "--max-retries 2 "
            "--request-timeout-seconds 10",
        )
        yield database_path


@pytest.mark.parametrize(
    "query",
    [
        "山旮旯",
        "山墳",
        "山窿",
        "山坑",
        "山坑水",
        "上便",
        "下便",
        "山坑",
        "山墳",
        "大馬",
    ],
)
@skip_if_ci()
def test_cmn_yue_dictionary_search_cli(cuhk_database_path: Path, query: str):
    """Test CUHK dictionary search CLI against a freshly built database."""
    with get_temp_file_path(".log") as log_file_path:
        run_cli_with_args(
            ScinoephileCli,
            "cmn_yue dictionary search "
            "-v "
            f"--log-file {log_file_path} "
            f"--database-path {cuhk_database_path} "
            f"--direction yue_to_cmn --limit 3 {query}",
        )
        output = log_file_path.read_text(encoding="utf-8")

    assert "Found " in output, output
    assert "Found 0 " not in output, output
    assert query in output, output
