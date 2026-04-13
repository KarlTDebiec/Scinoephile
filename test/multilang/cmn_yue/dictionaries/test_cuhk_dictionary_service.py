#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.cmn_yue.dictionaries.cuhk.CuhkDictionaryService."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import AbstractContextManager, nullcontext
from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.multilang.cmn_yue.dictionaries.cuhk import CuhkDictionaryService
from scinoephile.multilang.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionarySqliteStore,
    LookupDirection,
)


@pytest.fixture
def database_path() -> Generator[Path]:
    """Provide a temporary SQLite database path."""
    with get_temp_file_path(".db") as temp_path:
        yield temp_path


@pytest.fixture
def sample_entries() -> list[DictionaryEntry]:
    """Provide deterministic dictionary entries for CUHK service tests."""
    return [
        DictionaryEntry(
            traditional="山坑",
            simplified="山坑",
            pinyin="shan1 keng1",
            jyutping="saan1 haang1",
            frequency=2.0,
            definitions=[
                DictionaryDefinition(text="gully"),
                DictionaryDefinition(text="mountain stream", label="noun"),
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
    ]


@pytest.fixture
def sample_source() -> DictionarySource:
    """Provide deterministic dictionary source metadata."""
    return DictionarySource(
        name="Test Dictionary",
        shortname="test",
        version="2026.04",
        description="Dictionary source used for CUHK service tests.",
        legal="BSD",
        link="https://example.com/dictionary",
        update_url="https://example.com/dictionary/update",
        other="fixture",
    )


@pytest.fixture
def service(
    database_path: Path,
    sample_entries: list[DictionaryEntry],
    sample_source: DictionarySource,
) -> CuhkDictionaryService:
    """Provide a CUHK service backed by deterministic SQLite fixture data."""
    store = DictionarySqliteStore(database_path=database_path)
    store.persist((sample_source, sample_entries))
    return CuhkDictionaryService(database_path=database_path)


def test_lookup_preserves_explicit_direction(
    service: CuhkDictionaryService,
    sample_entries: list[DictionaryEntry],
):
    """Keep explicit-direction lookup available for LLM tooling."""
    assert service.lookup("shan1 keng1", LookupDirection.CMN_TO_YUE, limit=5) == [
        sample_entries[0],
        sample_entries[1],
    ]


@pytest.mark.parametrize(
    ("query", "expected", "expectation"),
    [
        ("山坑", ["山坑"], nullcontext()),
        ("shān kēng", ["山坑", "山坑水"], nullcontext()),
        ("saan1 haang1", ["山坑", "山坑水"], nullcontext()),
        (
            "gully",
            None,
            pytest.raises(
                ValueError,
                match="Could not infer a supported lookup format",
            ),
        ),
    ],
)
def test_lookup_inferred(
    service: CuhkDictionaryService,
    query: str,
    expected: list[str] | None,
    expectation: AbstractContextManager[object],
):
    """Infer searchable query formats or reject unsupported queries."""
    with expectation:
        entries = service.lookup_inferred(query, limit=5)
        assert [entry.traditional for entry in entries] == expected
