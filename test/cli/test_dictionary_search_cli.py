#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionarySearchCli."""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import ExitStack
from pathlib import Path

import pytest

from scinoephile.cli import DictionaryCli, DictionarySearchCli, ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from test.helpers import (
    assert_cli_help,
    assert_cli_usage,
    skip_if_ci,
    skip_if_no_network,
)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionarySearchCli,),
        (DictionaryCli, DictionarySearchCli),
        (ScinoephileCli, DictionaryCli, DictionarySearchCli),
    ],
)
def test_dictionary_search_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary search CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (DictionarySearchCli,),
        (DictionaryCli, DictionarySearchCli),
        (ScinoephileCli, DictionaryCli, DictionarySearchCli),
    ],
)
def test_dictionary_search_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary search CLI usage output."""
    assert_cli_usage(cli)


@pytest.fixture(scope="module")
def cuhk_database_path() -> Generator[Path]:
    """Build a temporary CUHK database for end-to-end search tests."""
    with ExitStack() as stack:
        cache_dir_path = stack.enter_context(get_temp_directory_path())
        database_path = stack.enter_context(get_temp_file_path(".db"))
        run_cli_with_args(
            ScinoephileCli,
            "dictionary build cuhk "
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


@pytest.fixture(scope="module")
def cuhk_traditional_query(cuhk_database_path: Path) -> str:
    """Fetch a traditional-only query token from the CUHK database."""
    with sqlite3.connect(cuhk_database_path) as connection:
        row = connection.execute(
            "SELECT traditional FROM entries WHERE traditional != simplified LIMIT 1"
        ).fetchone()
    if row is None:
        pytest.skip("No distinctive traditional entries available for search test.")
    return str(row[0])


@skip_if_ci()
@skip_if_no_network()
def test_dictionary_search_cli_traditional(
    cuhk_traditional_query: str, cuhk_database_path: Path
):
    """Test dictionary search CLI using an unambiguous traditional query."""
    with get_temp_file_path(".log") as log_file_path:
        run_cli_with_args(
            ScinoephileCli,
            "dictionary search "
            "-v "
            f"--log-file {log_file_path} "
            f"--database-path {cuhk_database_path} "
            f"--limit 3 {cuhk_traditional_query}",
        )
        output = log_file_path.read_text(encoding="utf-8")

    assert "Found " in output, output
    assert "Found 0 " not in output, output
    assert cuhk_traditional_query in output, output
