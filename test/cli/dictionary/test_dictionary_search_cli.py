#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionarySearchCli."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import AbstractContextManager, nullcontext
from os import environ
from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.dictionary.dictionary_cli import DictionaryCli
from scinoephile.cli.dictionary.dictionary_search_cli import DictionarySearchCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_directory_path, get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.multilang.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionarySqliteStore,
)
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (DictionarySearchCli,),
        (DictionaryCli, DictionarySearchCli),
        (ScinoephileCli, DictionaryCli, DictionarySearchCli),
    ],
)
def test_dictionary_search_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test dictionary search CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
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
    """Test dictionary search CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.fixture(scope="module")
def dictionary_database_dir_path() -> Generator[Path]:
    """Build temporary databases for end-to-end search tests."""
    with get_temp_directory_path() as dir_path:
        cache_dir_path = dir_path / "scinoephile" / "dictionaries"
        cuhk_database_path = cache_dir_path / "cuhk" / "cuhk.db"
        gzzj_database_path = cache_dir_path / "gzzj" / "gzzj.db"

        store = DictionarySqliteStore(database_path=cuhk_database_path)
        store.persist(
            (
                DictionarySource(
                    name="Test Dictionary",
                    shortname="test",
                    version="2026.04",
                    description="Dictionary source used for CLI tests.",
                    legal="BSD",
                    link="https://example.com/dictionary",
                    update_url="https://example.com/dictionary/update",
                    other="fixture",
                ),
                [
                    DictionaryEntry(
                        traditional="山坑",
                        simplified="山坑",
                        pinyin="shan1 keng1",
                        jyutping="saan1 haang1",
                        frequency=2.0,
                        definitions=[
                            DictionaryDefinition(text="gully"),
                            DictionaryDefinition(
                                text="mountain stream",
                                label="noun",
                            ),
                        ],
                    ),
                    DictionaryEntry(
                        traditional="共享",
                        simplified="共享",
                        pinyin="gong4 xiang3",
                        jyutping="gung6 hoeng2",
                        frequency=3.0,
                        definitions=[DictionaryDefinition(text="cuhk definition")],
                    ),
                    DictionaryEntry(
                        traditional="山坑水",
                        simplified="山坑水",
                        pinyin="shan1 keng1 shui3",
                        jyutping="saan1 haang1 seoi2",
                        frequency=1.0,
                        definitions=[DictionaryDefinition(text="stream water")],
                    ),
                ],
            )
        )

        store = DictionarySqliteStore(database_path=gzzj_database_path)
        store.persist(
            (
                DictionarySource(
                    name="Test GZZJ",
                    shortname="gzzj",
                    version="2026.04",
                    description="GZZJ source used for CLI tests.",
                    legal="BSD",
                    link="https://example.com/gzzj",
                    update_url="https://example.com/gzzj/update",
                    other="fixture",
                ),
                [
                    DictionaryEntry(
                        traditional="仇",
                        simplified="仇",
                        pinyin="qiu2",
                        jyutping="kau4",
                        frequency=1.0,
                        definitions=[
                            DictionaryDefinition(text="surname", label="釋義"),
                            DictionaryDefinition(text="又", label="讀音標記"),
                        ],
                    ),
                    DictionaryEntry(
                        traditional="共享",
                        simplified="共享",
                        pinyin="gong4 xiang3",
                        jyutping="gung6 hoeng2",
                        frequency=1.0,
                        definitions=[DictionaryDefinition(text="gzzj definition")],
                    ),
                ],
            )
        )
        yield dir_path


@pytest.mark.parametrize(
    ("query", "expected_output", "expectation"),
    [
        ("山坑", "山坑", nullcontext()),
        ("shān'kēng", "shān'kēng", nullcontext()),
        ("saan1haang1", "saan1haang1", nullcontext()),
        ("山坑水", "山坑水", nullcontext()),
        (
            "gully",
            "Unsupported query 'gully'",
            pytest.raises(SystemExit, match="1"),
        ),
    ],
)
def test_dictionary_search_cli(
    dictionary_database_dir_path: Path,
    query: str,
    expected_output: str,
    expectation: AbstractContextManager[object],
):
    """Test dictionary search CLI against a freshly built database.

    Arguments:
        dictionary_database_dir_path: directory containing fixture dictionaries
        query: query text to search
        expected_output: text expected in log output
        expectation: expected context manager for success or failure
    """
    database_path = (
        dictionary_database_dir_path
        / "scinoephile"
        / "dictionaries"
        / "cuhk"
        / "cuhk.db"
    )
    with get_temp_file_path(".log") as log_file_path:
        with expectation:
            run_cli_with_args(
                DictionarySearchCli,
                "-v "
                f"--log-file {log_file_path} "
                "--dictionary-name cuhk "
                f"--database-path {database_path} "
                f"--limit 3 {query}",
            )
        output = log_file_path.read_text(encoding="utf-8")

    if isinstance(expectation, type(nullcontext())):
        assert "Found " in output, output
        assert "Found 0 " not in output, output
    assert expected_output in output, output


def test_dictionary_search_cli_all_dictionaries(dictionary_database_dir_path: Path):
    """Test dictionary search can aggregate across installed dictionaries.

    Arguments:
        dictionary_database_dir_path: directory containing fixture dictionaries
    """
    with get_temp_file_path(".log") as log_file_path:
        with patch.dict(
            environ, {"SCINOEPHILE_CACHE_DIR": str(dictionary_database_dir_path)}
        ):
            run_cli_with_args(
                DictionarySearchCli,
                f"-v --log-file {log_file_path} --dictionary-name all --limit 3 仇",
            )
            output = log_file_path.read_text(encoding="utf-8")

    assert "仇" in output, output


def test_dictionary_search_cli_all_dictionaries_merges_definitions(
    dictionary_database_dir_path: Path,
):
    """Test dictionary search preserves definitions from multiple dictionaries.

    Arguments:
        dictionary_database_dir_path: directory containing fixture dictionaries
    """
    with get_temp_file_path(".log") as log_file_path:
        with patch.dict(
            environ, {"SCINOEPHILE_CACHE_DIR": str(dictionary_database_dir_path)}
        ):
            run_cli_with_args(
                DictionarySearchCli,
                f"-v --log-file {log_file_path} --dictionary-name all --limit 3 共享",
            )
            output = log_file_path.read_text(encoding="utf-8")

    assert "cuhk definition" in output, output
    assert "gzzj definition" in output, output


def test_dictionary_search_cli_all_dictionaries_database_path_is_usage_error():
    """Test aggregate search rejects an explicit database path as a usage error."""
    with get_temp_directory_path() as temp_dir_path:
        database_path = temp_dir_path / "existing.db"
        database_path.touch()
        with pytest.raises(SystemExit, match="2"):
            run_cli_with_args(
                DictionarySearchCli,
                f"--database-path {database_path} --dictionary-name all 共享",
            )
