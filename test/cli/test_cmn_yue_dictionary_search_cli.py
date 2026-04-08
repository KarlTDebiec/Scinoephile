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
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionarySqliteStore,
)
from test.helpers import assert_cli_help, assert_cli_usage


def _build_dictionary_database(
    database_path: Path,
    *,
    source_name: str,
    source_shortname: str,
    definition_text: str,
):
    """Build a synthetic dictionary SQLite database for search tests.

    Arguments:
        database_path: output SQLite database path
        source_name: full source name
        source_shortname: short source name
        definition_text: definition text to persist
    """
    source = DictionarySource(
        name=source_name,
        shortname=source_shortname,
        version="2026.04",
        description=f"Synthetic dictionary source {source_shortname}",
        legal="Synthetic test data",
        link="https://example.com",
        update_url="https://example.com/update",
        other="words",
    )
    entry = DictionaryEntry(
        traditional="山坑",
        simplified="山坑",
        pinyin="shan1 keng1",
        jyutping="saan1 haang1",
        frequency=5.0,
        definitions=[
            DictionaryDefinition(
                text=definition_text,
                label="釋義",
            )
        ],
    )
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((source, [entry]))


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
    """Test dictionary search CLI help output."""
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
    """Test dictionary search CLI usage output."""
    assert_cli_usage(cli)


@pytest.fixture(scope="module")
def dictionary_database_paths() -> Generator[tuple[Path, Path]]:
    """Build two synthetic dictionary databases for end-to-end search tests."""
    with ExitStack() as stack:
        database_one_path = stack.enter_context(get_temp_file_path(".db"))
        database_two_path = stack.enter_context(get_temp_file_path(".db"))
        _build_dictionary_database(
            database_one_path,
            source_name="Synthetic Source One",
            source_shortname="SYNA",
            definition_text="synthetic definition one",
        )
        _build_dictionary_database(
            database_two_path,
            source_name="Synthetic Source Two",
            source_shortname="SYNB",
            definition_text="synthetic definition two",
        )
        yield database_one_path, database_two_path


def test_cmn_yue_dictionary_search_cli_aggregates_sources(
    dictionary_database_paths: tuple[Path, Path],
):
    """Test dictionary search CLI aggregates results across explicit databases."""
    database_one_path, database_two_path = dictionary_database_paths
    with get_temp_file_path(".log") as log_file_path:
        run_cli_with_args(
            ScinoephileCli,
            "cmn_yue dictionary search "
            "-v "
            f"--log-file {log_file_path} "
            f"--database-path {database_one_path} "
            f"--database-path {database_two_path} "
            "--direction yue_to_cmn --limit 10 山坑",
        )
        output = log_file_path.read_text(encoding="utf-8")

    assert "Found 2 match(es)" in output, output
    assert "[SYNA]" in output, output
    assert "[SYNB]" in output, output
    assert "synthetic definition one" in output, output
    assert "synthetic definition two" in output, output


def test_cmn_yue_dictionary_search_cli_filters_sources(
    dictionary_database_paths: tuple[Path, Path],
):
    """Test dictionary search CLI filters results to one requested source."""
    database_one_path, database_two_path = dictionary_database_paths
    with get_temp_file_path(".log") as log_file_path:
        run_cli_with_args(
            ScinoephileCli,
            "cmn_yue dictionary search "
            "-v "
            f"--log-file {log_file_path} "
            f"--database-path {database_one_path} "
            f"--database-path {database_two_path} "
            "--source synb --direction yue_to_cmn --limit 10 山坑",
        )
        output = log_file_path.read_text(encoding="utf-8")

    assert "Found 1 match(es)" in output, output
    assert "[SYNA]" not in output, output
    assert "[SYNB]" in output, output
    assert "synthetic definition two" in output, output
