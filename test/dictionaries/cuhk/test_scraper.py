#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CUHK dictionary scraping cache behavior."""

from __future__ import annotations

from pathlib import Path
from time import time
from unittest.mock import Mock

from scinoephile.dictionaries.cuhk.scraper import CuhkDictionaryScraper
from test.helpers.files import set_mtime


def test_fetch_text_overwrites_matching_cache(tmp_path: Path):
    """Test cache overwrite fetches and replaces a matching CUHK response."""
    response = Mock(text="fresh")
    session = Mock()
    session.get.return_value = response
    scraper = CuhkDictionaryScraper(
        cache_root_path=tmp_path,
        min_delay_seconds=0.0,
        max_delay_seconds=0.0,
        overwrite_cache=True,
        session=session,
    )
    cache_path = scraper.discovery_cache_dir_path / "terms.html"
    cache_path.write_text("stale", encoding="utf-8")

    result = scraper._fetch_text(
        "https://example.test/terms",
        cache_path=cache_path,
        use_cache=True,
    )

    assert result == "fresh"
    assert cache_path.read_text(encoding="utf-8") == "fresh"
    session.get.assert_called_once_with(
        "https://example.test/terms",
        timeout=30.0,
    )


def test_fetch_text_marks_matching_cache_used(tmp_path: Path):
    """Test a CUHK response cache hit refreshes its pruning timestamp."""
    session = Mock()
    scraper = CuhkDictionaryScraper(cache_root_path=tmp_path, session=session)
    cache_path = scraper.discovery_cache_dir_path / "terms.html"
    cache_path.write_text("cached", encoding="utf-8")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(cache_path, old_timestamp)

    result = scraper._fetch_text(
        "https://example.test/terms",
        cache_path=cache_path,
        use_cache=True,
    )

    assert result == "cached"
    assert cache_path.stat().st_mtime > old_timestamp
    session.get.assert_not_called()


def test_fetch_text_regenerates_invalid_cache(tmp_path: Path):
    """Test an unreadable CUHK response cache is treated as a miss."""
    response = Mock(text="fresh")
    session = Mock()
    session.get.return_value = response
    scraper = CuhkDictionaryScraper(
        cache_root_path=tmp_path,
        min_delay_seconds=0.0,
        max_delay_seconds=0.0,
        session=session,
    )
    cache_path = scraper.discovery_cache_dir_path / "terms.html"
    cache_path.write_bytes(b"\xff")

    result = scraper._fetch_text(
        "https://example.test/terms",
        cache_path=cache_path,
        use_cache=True,
    )

    assert result == "fresh"
    assert cache_path.read_text(encoding="utf-8") == "fresh"


def test_cache_namespaces_are_flat(tmp_path: Path):
    """Test CUHK discovery and word pages use independent flat namespaces."""
    scraper = CuhkDictionaryScraper(cache_root_path=tmp_path)

    assert scraper.discovery_cache_dir_path == tmp_path / "cuhk-discovery"
    assert scraper.scraped_cache_dir_path == tmp_path / "cuhk-pages"
