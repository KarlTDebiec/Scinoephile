#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.cmn_yue.dictionaries.service."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import ExitStack
from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionarySqliteStore,
    LookupDirection,
)
from scinoephile.multilang.cmn_yue.dictionaries.service import CmnYueDictionaryService


def _build_dictionary_database(
    database_path: Path,
    *,
    source_name: str,
    source_shortname: str,
    definition_text: str,
):
    """Build a synthetic dictionary SQLite database for service tests.

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


@pytest.fixture()
def dictionary_database_paths() -> Generator[tuple[Path, Path]]:
    """Build two synthetic dictionary databases for aggregate lookup tests."""
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


def test_cmn_yue_dictionary_service_aggregates_sources(
    dictionary_database_paths: tuple[Path, Path],
):
    """Test aggregate lookup across multiple explicit dictionary databases."""
    service = CmnYueDictionaryService(database_paths=list(dictionary_database_paths))

    results = service.lookup(
        query="山坑",
        direction=LookupDirection.YUE_TO_CMN,
        limit=10,
    )

    assert [result.source_id for result in results] == ["syna", "synb"]
    assert [result.entry.definitions[0].text for result in results] == [
        "synthetic definition one",
        "synthetic definition two",
    ]


def test_cmn_yue_dictionary_service_filters_explicit_sources(
    dictionary_database_paths: tuple[Path, Path],
):
    """Test aggregate lookup filtering for one requested explicit source."""
    service = CmnYueDictionaryService(database_paths=list(dictionary_database_paths))

    results = service.lookup(
        query="山坑",
        direction=LookupDirection.YUE_TO_CMN,
        limit=10,
        source_ids=["synb"],
    )

    assert len(results) == 1
    assert results[0].source_id == "synb"
    assert results[0].entry.definitions[0].text == "synthetic definition two"


def test_cmn_yue_dictionary_service_reports_missing_explicit_source(
    dictionary_database_paths: tuple[Path, Path],
):
    """Test aggregate lookup errors when an explicit source filter is missing."""
    service = CmnYueDictionaryService(database_paths=list(dictionary_database_paths))

    with pytest.raises(
        FileNotFoundError,
        match="Requested dictionary source\\(s\\) not found",
    ):
        service.lookup(
            query="山坑",
            direction=LookupDirection.YUE_TO_CMN,
            limit=10,
            source_ids=["missing"],
        )
