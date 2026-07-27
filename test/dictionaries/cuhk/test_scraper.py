#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CUHK dictionary scraping cache behavior."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import MonkeyPatch

from scinoephile.dictionaries.cuhk.cache import CuhkResponseCache
from scinoephile.dictionaries.cuhk.scraper import CuhkDictionaryScraper
from test.helpers.files import set_mtime


def test_response_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Test overwrite refreshes a matching CUHK response once per instance."""
    cache = CuhkResponseCache(tmp_path, "cuhk-discovery")
    cache.save("terms", "stale")
    overwrite_cache = CuhkResponseCache(tmp_path, "cuhk-discovery", True)

    assert overwrite_cache.load("terms") is None
    overwrite_cache.save("terms", "fresh")

    assert overwrite_cache.load("terms") == "fresh"


def test_response_cache_marks_matching_entry_used(tmp_path: Path):
    """Test a CUHK response cache hit refreshes its pruning timestamp."""
    cache = CuhkResponseCache(tmp_path, "cuhk-discovery")
    cache_path = cache.save("terms", "cached")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(cache_path, old_timestamp)

    result = cache.load("terms")

    assert result == "cached"
    assert cache_path.stat().st_mtime > old_timestamp


def test_response_cache_discards_invalid_entry(tmp_path: Path):
    """Test an unreadable CUHK response cache is treated as a miss."""
    cache = CuhkResponseCache(tmp_path, "cuhk-discovery")
    cache_path = cache.get_path("terms")
    cache_path.parent.mkdir()
    cache_path.write_bytes(b"\xff")

    assert cache.load("terms") is None
    assert not cache_path.exists()


def test_response_cache_namespaces_are_flat(tmp_path: Path):
    """Test CUHK discovery and word pages use independent flat namespaces."""
    scraper = CuhkDictionaryScraper(cache_root_path=tmp_path)

    assert scraper.discovery_cache.cache_dir_path == tmp_path / "cuhk-discovery"
    assert scraper.scraped_cache.cache_dir_path == tmp_path / "cuhk-pages"


def test_response_cache_paths_include_version(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
):
    """Test CUHK response cache paths differ between cache versions."""
    cache = CuhkResponseCache(tmp_path, "cuhk-discovery")
    first_cache_path = cache.get_path("terms")

    monkeypatch.setattr("scinoephile.dictionaries.cuhk.cache._CACHE_VERSION", 2)

    assert cache.get_path("terms") != first_cache_path
