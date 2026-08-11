#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CUHK dictionary scraping cache behavior."""

from __future__ import annotations

from pathlib import Path
from time import time
from unittest.mock import Mock

from pytest import MonkeyPatch, raises

from scinoephile.dictionaries.cache_namespace import DictionariesCacheNamespace
from scinoephile.dictionaries.cuhk.cache import CuhkResponseCache
from scinoephile.dictionaries.cuhk.scraper import CuhkDictionaryScraper
from test.helpers.files import set_mtime


def test_response_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Test overwrite refreshes a matching CUHK response once per instance."""
    cache = CuhkResponseCache(tmp_path, DictionariesCacheNamespace.CUHK_DISCOVERY)
    cache.save("terms", "stale")
    overwrite_cache = CuhkResponseCache(
        tmp_path, DictionariesCacheNamespace.CUHK_DISCOVERY, True
    )

    assert overwrite_cache.load("terms") is None
    overwrite_cache.save("terms", "fresh")

    assert overwrite_cache.load("terms") == "fresh"


def test_response_cache_marks_matching_entry_used(tmp_path: Path):
    """Test a CUHK response cache hit refreshes its pruning timestamp."""
    cache = CuhkResponseCache(tmp_path, DictionariesCacheNamespace.CUHK_DISCOVERY)
    cache_path = cache.save("terms", "cached")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(cache_path, old_timestamp)

    result = cache.load("terms")

    assert result == "cached"
    assert cache_path.stat().st_mtime > old_timestamp


def test_response_cache_discards_invalid_entry(tmp_path: Path):
    """Test an unreadable CUHK response cache is treated as a miss."""
    cache = CuhkResponseCache(tmp_path, DictionariesCacheNamespace.CUHK_DISCOVERY)
    cache_path = cache.get_path("terms")
    cache_path.parent.mkdir()
    cache_path.write_bytes(b"\xff")

    assert cache.load("terms") is None
    assert not cache_path.exists()


def test_response_cache_namespaces_follow_package_ownership(tmp_path: Path):
    """Test CUHK response namespaces follow their producing package."""
    scraper = CuhkDictionaryScraper(cache_root_path=tmp_path)

    assert scraper.discovery_cache.cache_dir_path == (
        tmp_path / "dictionaries/cuhk/discovery"
    )
    assert scraper.scraped_cache.cache_dir_path == (
        tmp_path / "dictionaries/cuhk/pages"
    )


def test_response_cache_paths_include_version(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Test CUHK response cache paths differ between cache versions."""
    cache = CuhkResponseCache(tmp_path, DictionariesCacheNamespace.CUHK_DISCOVERY)
    first_cache_path = cache.get_path("terms")

    monkeypatch.setattr("scinoephile.dictionaries.cuhk.cache._CACHE_VERSION", 2)

    assert cache.get_path("terms") != first_cache_path


def test_response_cache_rejects_unsafe_stem(tmp_path: Path):
    """Test CUHK response stems may not escape the cache directory."""
    cache = CuhkResponseCache(tmp_path, DictionariesCacheNamespace.CUHK_DISCOVERY)

    with raises(ValueError, match="single contained filename"):
        cache.get_path("../terms")


def test_parse_scraped_pages_loads_through_cache(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test cached CUHK pages are validated and marked used before parsing."""
    scraper = CuhkDictionaryScraper(cache_root_path=tmp_path)
    valid_path = scraper.scraped_cache.save("valid", "valid")
    invalid_path = scraper.scraped_cache.get_path("invalid")
    invalid_path.parent.mkdir()
    invalid_path.write_bytes(b"\xff")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(valid_path, old_timestamp)
    parse_word_html = Mock(return_value=None)
    monkeypatch.setattr(scraper, "parse_word_html", parse_word_html)

    assert scraper.parse_scraped_pages() == []
    assert valid_path.stat().st_mtime > old_timestamp
    assert not invalid_path.exists()
    parse_word_html.assert_called_once_with("valid", valid_path)
