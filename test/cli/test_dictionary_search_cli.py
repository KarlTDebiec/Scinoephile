#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionarySearchCli."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from scinoephile.cli import (
    DictionaryCli,
    DictionarySearchCli,
    ScinoephileCli,
)
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
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
    """Test CUHK dictionary search CLI help output."""
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
    """Test CUHK dictionary search CLI usage output."""
    assert_cli_usage(cli)


@pytest.fixture(scope="module")
def cuhk_database_path() -> Generator[Path]:
    """Build a temporary CUHK-like database for end-to-end search tests."""
    with get_temp_file_path(".db") as database_path:
        store = DictionarySqliteStore(database_path=database_path)
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
        yield database_path


@pytest.mark.parametrize(
    "query",
    [
        "山坑",
        "shān'kēng",
        "saan1haang1",
        "山坑水",
    ],
)
def test_dictionary_search_cli(cuhk_database_path: Path, query: str):
    """Test CUHK dictionary search CLI against a freshly built database."""
    with get_temp_file_path(".log") as log_file_path:
        run_cli_with_args(
            ScinoephileCli,
            "dictionary search "
            "-v "
            f"--log-file {log_file_path} "
            f"--database-path {cuhk_database_path} "
            f"--limit 3 {query}",
        )
        output = log_file_path.read_text(encoding="utf-8")

    assert "Found " in output, output
    assert "Found 0 " not in output, output
    assert query in output, output
