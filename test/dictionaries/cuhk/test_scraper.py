#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of CUHK dictionary scraping cache behavior."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from scinoephile.dictionaries.cuhk.scraper import CuhkDictionaryScraper


def test_fetch_text_overwrites_matching_cache(tmp_path: Path):
    """Test cache overwrite fetches and replaces a matching CUHK response."""
    cache_path = tmp_path / "discovery" / "terms.html"
    cache_path.parent.mkdir()
    cache_path.write_text("stale", encoding="utf-8")
    response = Mock(text="fresh")
    session = Mock()
    session.get.return_value = response
    scraper = CuhkDictionaryScraper(
        cache_dir_path=tmp_path,
        min_delay_seconds=0.0,
        max_delay_seconds=0.0,
        overwrite_cache=True,
        session=session,
    )

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
