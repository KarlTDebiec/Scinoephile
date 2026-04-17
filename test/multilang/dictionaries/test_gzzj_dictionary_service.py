#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.dictionaries.gzzj.GzzjDictionaryService."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import AbstractContextManager, nullcontext
from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.multilang.dictionaries.gzzj import GzzjDictionaryService


@pytest.fixture
def source_json_path() -> Generator[Path]:
    """Provide a minimal temporary GZZJ source JSON file."""
    with get_temp_file_path(".json") as temp_path:
        temp_path.write_text(
            (
                '[{"頁": 1, "字頭": ["仇"], "義項": ['
                '{"釋義": "～敵．～恨", "讀音": ['
                '{"粵拼讀音": "sau4", "讀音標記": null, '
                '"_校訂補充": {"校訂註": null}}]}, '
                '{"釋義": "姓", "讀音": ['
                '{"粵拼讀音": "kau4", "讀音標記": "又", '
                '"_校訂補充": {"校訂註": "異讀"}}]}], '
                '"_校訂補充": {"異體": ["讎"]}}]'
            ),
            encoding="utf-8",
        )
        yield temp_path


@pytest.fixture
def database_path() -> Generator[Path]:
    """Provide a temporary SQLite database path."""
    with get_temp_file_path(".db") as temp_path:
        yield temp_path


@pytest.fixture
def service(database_path: Path, source_json_path: Path) -> GzzjDictionaryService:
    """Provide a GZZJ service backed by deterministic JSON fixture data."""
    service = GzzjDictionaryService(
        database_path=database_path,
        source_json_path=source_json_path,
    )
    service.build(overwrite=True)
    return service


@pytest.mark.parametrize(
    ("query", "expected", "expectation"),
    [
        ("", [], nullcontext()),
        ("仇", ["仇", "仇"], nullcontext()),
        ("讎", ["讎", "讎"], nullcontext()),
        ("kau4", ["仇", "讎"], nullcontext()),
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
def test_lookup(
    service: GzzjDictionaryService,
    query: str,
    expected: list[str] | None,
    expectation: AbstractContextManager[object],
):
    """Infer searchable query formats or reject unsupported queries."""
    with expectation:
        entries = service.lookup(query, limit=10)
        assert [entry.traditional for entry in entries] == expected


def test_build_normalizes_list_valued_headwords(service: GzzjDictionaryService):
    """Persist normalized scalar text when source headwords are list-valued."""
    entries = service.lookup("仇", limit=10)

    assert [entry.traditional for entry in entries] == ["仇", "仇"]
    assert [entry.simplified for entry in entries] == ["仇", "仇"]
    assert [entry.pinyin for entry in entries] == ["chou2", "chou2"]
