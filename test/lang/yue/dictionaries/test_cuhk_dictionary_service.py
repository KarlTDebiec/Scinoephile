#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CUHK dictionary service and parser."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from scinoephile.lang.yue.dictionaries.cuhk import (
    CuhkDictionaryBuilder,
    CuhkDictionaryService,
    LookupDirection,
)
from scinoephile.lang.yue.dictionaries.cuhk.models import DictionarySource
from scinoephile.lang.yue.dictionaries.cuhk.sqlite_schema import (
    create_tables,
    drop_tables,
    generate_indices,
    insert_definition,
    insert_entry,
    insert_source,
    write_database_version,
)


def _seed_dictionary_database(database_path: Path):
    """Seed a minimal dictionary database for lookup tests.

    Arguments:
        database_path: sqlite database path
    """
    with sqlite3.connect(database_path) as connection:
        cursor = connection.cursor()
        write_database_version(cursor)
        drop_tables(cursor)
        create_tables(cursor)

        source_id = insert_source(
            cursor,
            DictionarySource(
                name="Test Source",
                shortname="TEST",
                version="1",
                description="Test dictionary",
                legal="Testing only",
                link="https://example.com",
                update_url="",
                other="",
            ),
        )
        entry_id = insert_entry(
            cursor,
            traditional="巴士",
            simplified="巴士",
            pinyin="ba1 shi4",
            jyutping="baa1 si6",
            frequency=0.0,
        )
        insert_definition(
            cursor,
            definition="bus",
            label="名詞",
            entry_id=entry_id,
            source_id=source_id,
        )
        generate_indices(cursor)
        connection.commit()


def test_lookup_missing_database_raises(tmp_path: Path):
    """Test lookup fails cleanly when local database is missing."""
    service = CuhkDictionaryService(
        cache_dir_path=tmp_path / "missing",
        auto_build_missing=False,
    )
    with pytest.raises(FileNotFoundError):
        service.lookup("巴士")


def test_lookup_mandarin_to_cantonese(tmp_path: Path):
    """Test Mandarin to Cantonese lookup using seeded SQLite data."""
    service = CuhkDictionaryService(
        cache_dir_path=tmp_path / "cuhk",
        auto_build_missing=False,
    )
    _seed_dictionary_database(service.database_path)

    results = service.lookup(
        "巴士",
        direction=LookupDirection.MANDARIN_TO_CANTONESE,
        limit=5,
    )
    assert len(results) == 1
    assert results[0].traditional == "巴士"
    assert results[0].jyutping == "baa1 si6"
    assert len(results[0].definitions) == 1
    assert results[0].definitions[0].text == "bus"


def test_lookup_cantonese_to_mandarin(tmp_path: Path):
    """Test Cantonese to Mandarin lookup using seeded SQLite data."""
    service = CuhkDictionaryService(
        cache_dir_path=tmp_path / "cuhk",
        auto_build_missing=False,
    )
    _seed_dictionary_database(service.database_path)

    results = service.lookup(
        "baa1 si6",
        direction=LookupDirection.CANTONESE_TO_MANDARIN,
        limit=5,
    )
    assert len(results) == 1
    assert results[0].simplified == "巴士"
    assert results[0].pinyin == "ba1 shi4"


def test_parse_word_file_applies_tone_mapping(tmp_path: Path):
    """Test parsing of CUHK page and 7/8/9 tone remapping."""
    builder = CuhkDictionaryBuilder(
        cache_dir_path=tmp_path / "cuhk",
        min_delay_seconds=0.0,
        max_delay_seconds=0.0,
    )

    html_path = builder.scraped_dir_path / "測試.html"
    html_path.write_text(
        """
        <html><body>
            <span class="ChiCharFix">測試</span>
            <span id="MainContent_repeaterRecord_lbl詞彙類別_0">名詞</span>
            <span id="MainContent_repeaterRecord_lbl粵語拼音_0">cak ce</span>
            <span id="MainContent_repeaterRecord_lbl聲調_0">7 8</span>
<span id="MainContent_repeaterRecord_repeaterTranslation_0_lblTranslation_0">
                test
            </span>
            <span id="MainContent_repeaterRecord_lblRemark_0">remark</span>
        </body></html>
        """,
        encoding="utf-8",
    )

    entry = builder.parse_word_file(html_path)
    assert entry is not None
    assert entry.traditional == "測試"
    assert entry.jyutping == "cak1 ce3"
    assert len(entry.definitions) == 2
    assert entry.definitions[0].label == "名詞"
    assert entry.definitions[1].label == "備註"
