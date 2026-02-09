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


class _DiscoverOnlyBuilder(CuhkDictionaryBuilder):
    """Builder test double that records fetched URLs."""

    def __init__(self, cache_dir_path: Path):
        """Initialize.

        Arguments:
            cache_dir_path: test cache directory path
        """
        super().__init__(
            cache_dir_path=cache_dir_path,
            min_delay_seconds=0.0,
            max_delay_seconds=0.0,
        )
        self.fetched_urls: list[str] = []

    def _fetch_text(self, url: str) -> str:  # noqa: PLR0911
        """Return deterministic HTML for discovery flow.

        Arguments:
            url: URL requested by discovery logic
        Returns:
            mock HTML page content
        """
        self.fetched_urls.append(url)
        if url.endswith("/Terms.aspx"):
            return """
                <html><body>
                    <div id="MainContent_panelTermsIndex">
                        <a href="Terms.aspx?target=名詞">valid category</a>
                        <a href="https://www.qef.org.hk/chinese/index.htm">external</a>
                    </div>
                </body></html>
            """
        if "target=" in url:
            return """
                <html><body>
                    <div id="MainContent_panelTermsQuery">
                        <a href="Word.aspx?id=1">巴士</a>
                        <a href="https://example.com/outside">外部</a>
                        <a href="Cover.aspx">封面</a>
                    </div>
                </body></html>
            """
        raise AssertionError(f"Unexpected URL fetched: {url}")


class _ForceRebuildBuilder(CuhkDictionaryBuilder):
    """Builder test double used to verify force-rebuild behavior."""

    def __init__(self, cache_dir_path: Path):
        """Initialize.

        Arguments:
            cache_dir_path: test cache directory path
        """
        super().__init__(
            cache_dir_path=cache_dir_path,
            min_delay_seconds=0.0,
            max_delay_seconds=0.0,
        )

    def discover_word_links(self) -> list[tuple[str, str]]:
        """Return deterministic word links."""
        return [("新詞", "https://apps.itsc.cuhk.edu.hk/hanyu/Page/Word.aspx?id=1")]

    def _fetch_text(self, url: str) -> str:
        """Return deterministic word HTML."""
        if "Word.aspx?id=1" not in url:
            raise AssertionError(f"Unexpected URL fetched: {url}")
        return """
            <html><body>
                <span class="ChiCharFix">新詞</span>
                <span id="MainContent_repeaterRecord_lbl詞彙類別_0">名詞</span>
                <span id="MainContent_repeaterRecord_lbl粵語拼音_0">san ci</span>
                <span id="MainContent_repeaterRecord_lbl聲調_0">1 4</span>
                <span
                    id="MainContent_repeaterRecord_repeaterTranslation_0_lblTranslation_0"
                >
                    new term
                </span>
            </body></html>
        """


def _seed_dictionary_database(database_path: Path):
    """Seed a minimal dictionary database for lookup tests.

    Arguments:
        database_path: sqlite database path
    """
    database_path.parent.mkdir(parents=True, exist_ok=True)
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
        bus_entry_id = insert_entry(
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
            entry_id=bus_entry_id,
            source_id=source_id,
        )
        insert_definition(
            cursor,
            definition="motor bus",
            label="名詞",
            entry_id=bus_entry_id,
            source_id=source_id,
        )

        stop_entry_id = insert_entry(
            cursor,
            traditional="巴士站",
            simplified="巴士站",
            pinyin="ba1 shi4 zhan4",
            jyutping="baa1 si6 zaam6",
            frequency=0.0,
        )
        insert_definition(
            cursor,
            definition="bus stop",
            label="名詞",
            entry_id=stop_entry_id,
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
    assert len(results[0].definitions) == 2
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
    assert len(results) == 2
    assert results[0].simplified == "巴士"
    assert results[0].pinyin == "ba1 shi4"
    assert len(results[0].definitions) == 2


def test_lookup_limit_applies_to_entries_not_join_rows(tmp_path: Path):
    """Test lookup limit is applied at entry level, not join-row level."""
    service = CuhkDictionaryService(
        cache_dir_path=tmp_path / "cuhk",
        auto_build_missing=False,
    )
    _seed_dictionary_database(service.database_path)

    results = service.lookup(
        "baa1 si6",
        direction=LookupDirection.CANTONESE_TO_MANDARIN,
        limit=1,
    )
    assert len(results) == 1
    assert results[0].traditional == "巴士"
    assert [definition.text for definition in results[0].definitions] == [
        "bus",
        "motor bus",
    ]


def test_lookup_nonpositive_limit_is_sanitized(tmp_path: Path):
    """Test non-positive lookup limit is sanitized to one result."""
    service = CuhkDictionaryService(
        cache_dir_path=tmp_path / "cuhk",
        auto_build_missing=False,
    )
    _seed_dictionary_database(service.database_path)

    results = service.lookup(
        "baa1 si6",
        direction=LookupDirection.CANTONESE_TO_MANDARIN,
        limit=-3,
    )
    assert len(results) == 1
    assert results[0].traditional == "巴士"


def test_lookup_escapes_like_wildcards(tmp_path: Path):
    """Test lookup treats `%` and `_` literally rather than as wildcards."""
    service = CuhkDictionaryService(
        cache_dir_path=tmp_path / "cuhk",
        auto_build_missing=False,
    )
    _seed_dictionary_database(service.database_path)

    mandarin_results = service.lookup(
        "%",
        direction=LookupDirection.MANDARIN_TO_CANTONESE,
        limit=10,
    )
    cantonese_results = service.lookup(
        "_",
        direction=LookupDirection.CANTONESE_TO_MANDARIN,
        limit=10,
    )

    assert mandarin_results == []
    assert cantonese_results == []


def test_parse_word_file_applies_tone_mapping(tmp_path: Path):
    """Test parsing of CUHK page and 7/8/9 tone remapping."""
    builder = CuhkDictionaryBuilder(
        cache_dir_path=tmp_path / "cuhk",
        min_delay_seconds=0.0,
        max_delay_seconds=0.0,
    )

    html_path = builder.scraped_dir_path / "測試.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
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


def test_parse_word_file_rejects_mismatched_jyutping(tmp_path: Path):
    """Test parser rejects pages with mismatched jyutping letters and tones."""
    builder = CuhkDictionaryBuilder(
        cache_dir_path=tmp_path / "cuhk",
        min_delay_seconds=0.0,
        max_delay_seconds=0.0,
    )

    html_path = builder.scraped_dir_path / "失配.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(
        """
        <html><body>
            <span class="ChiCharFix">失配</span>
            <span id="MainContent_repeaterRecord_lbl詞彙類別_0">名詞</span>
            <span id="MainContent_repeaterRecord_lbl粵語拼音_0">sat pui</span>
            <span id="MainContent_repeaterRecord_lbl聲調_0">1</span>
            <span
                id="MainContent_repeaterRecord_repeaterTranslation_0_lblTranslation_0"
            >
                mismatch
            </span>
        </body></html>
        """,
        encoding="utf-8",
    )

    assert builder.parse_word_file(html_path) is None


def test_discover_word_links_filters_external_category_links(tmp_path: Path):
    """Test discovery ignores non-CUHK/invalid category and word anchors."""
    builder = _DiscoverOnlyBuilder(cache_dir_path=tmp_path / "cuhk")
    links = builder.discover_word_links()

    assert len(links) == 1
    assert links[0][0] == "巴士"
    assert links[0][1] == "https://apps.itsc.cuhk.edu.hk/hanyu/Page/Word.aspx?id=1"
    assert builder.fetched_urls[0].endswith("/Terms.aspx")
    assert all("qef.org.hk" not in url for url in builder.fetched_urls)


def test_build_force_rebuild_clears_stale_scraped_pages(tmp_path: Path):
    """Test force rebuild removes stale HTML files before parsing."""
    builder = _ForceRebuildBuilder(cache_dir_path=tmp_path / "cuhk")
    stale_path = builder.scraped_dir_path / "舊詞.html"
    stale_path.parent.mkdir(parents=True, exist_ok=True)
    stale_path.write_text(
        """
        <html><body>
            <span class="ChiCharFix">舊詞</span>
            <span id="MainContent_repeaterRecord_lbl詞彙類別_0">名詞</span>
            <span id="MainContent_repeaterRecord_lbl粵語拼音_0">gau ci</span>
            <span id="MainContent_repeaterRecord_lbl聲調_0">3 4</span>
        </body></html>
        """,
        encoding="utf-8",
    )

    database_path = builder.build(force_rebuild=True)

    assert database_path.exists()
    assert not stale_path.exists()
    entries = builder.parse_scraped_pages()
    assert len(entries) == 1
    assert entries[0].traditional == "新詞"


def test_insert_entry_returns_existing_id_for_duplicate():
    """Test duplicate entry insert returns stable existing entry ID."""
    with sqlite3.connect(":memory:") as connection:
        cursor = connection.cursor()
        write_database_version(cursor)
        create_tables(cursor)

        first_id = insert_entry(
            cursor,
            traditional="巴士",
            simplified="巴士",
            pinyin="ba1 shi4",
            jyutping="baa1 si6",
            frequency=0.0,
        )
        duplicate_id = insert_entry(
            cursor,
            traditional="巴士",
            simplified="巴士",
            pinyin="ba1 shi4",
            jyutping="baa1 si6",
            frequency=0.0,
        )
        assert duplicate_id == first_id


def test_insert_definition_returns_existing_id_for_duplicate():
    """Test duplicate definition insert returns stable existing definition ID."""
    with sqlite3.connect(":memory:") as connection:
        cursor = connection.cursor()
        write_database_version(cursor)
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

        first_id = insert_definition(
            cursor,
            definition="bus",
            label="名詞",
            entry_id=entry_id,
            source_id=source_id,
        )
        duplicate_id = insert_definition(
            cursor,
            definition="bus",
            label="名詞",
            entry_id=entry_id,
            source_id=source_id,
        )
        assert duplicate_id == first_id
