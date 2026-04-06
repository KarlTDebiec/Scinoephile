#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the CUHK dictionary service."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import call, patch

from scinoephile.core.dictionaries import DictionaryEntry, LookupDirection
from scinoephile.multilang.cmn_yue.dictionaries.cuhk import CuhkDictionaryService


def _make_entry() -> DictionaryEntry:
    """Get a representative dictionary entry for tests.

    Returns:
        representative dictionary entry
    """
    return DictionaryEntry(
        traditional="上便",
        simplified="上便",
        pinyin="shang4 bian4",
        jyutping="soeng6 bin6",
    )


def test_cuhk_dictionary_service_lookup_normalizes_cmn_pinyin(tmp_path: Path):
    """Test CUHK service normalizes accented pinyin before lookup.

    Arguments:
        tmp_path: temporary test directory
    """
    database_path = tmp_path / "cuhk.db"
    database_path.touch()
    service = CuhkDictionaryService(
        database_path=database_path,
        scraper_kwargs={"cache_dir_path": tmp_path / "cache"},
    )
    expected = [_make_entry()]

    with patch.object(service.database, "lookup", return_value=expected) as mock_lookup:
        output = service.lookup(
            "Shàng biàn",
            direction=LookupDirection.CMN_TO_YUE,
            limit=3,
        )

    assert output == expected
    mock_lookup.assert_called_once_with("shang4 bian4", LookupDirection.CMN_TO_YUE, 3)


def test_cuhk_dictionary_service_lookup_tries_yale_variants(tmp_path: Path):
    """Test CUHK service tries Yale-derived Jyutping variants until one matches.

    Arguments:
        tmp_path: temporary test directory
    """
    database_path = tmp_path / "cuhk.db"
    database_path.touch()
    service = CuhkDictionaryService(
        database_path=database_path,
        scraper_kwargs={"cache_dir_path": tmp_path / "cache"},
    )
    expected = [_make_entry()]

    with patch(
        "scinoephile.multilang.cmn_yue.dictionaries.cuhk.service.get_yue_jyutping_query_strings",
        return_value=["soeng6 ban6", "soeng6 bin6"],
    ):
        with patch.object(
            service.database,
            "lookup",
            side_effect=[[], expected],
        ) as mock_lookup:
            output = service.lookup(
                "séung'bihn",
                direction=LookupDirection.YUE_TO_CMN,
                limit=2,
            )

    assert output == expected
    assert mock_lookup.call_args_list == [
        call("soeng6 ban6", LookupDirection.YUE_TO_CMN, 2),
        call("soeng6 bin6", LookupDirection.YUE_TO_CMN, 2),
    ]


def test_cuhk_dictionary_service_build_skips_existing_database_when_not_overwriting(
    tmp_path: Path,
):
    """Test CUHK service preserves an existing database during limited builds.

    Arguments:
        tmp_path: temporary test directory
    """
    database_path = tmp_path / "cuhk.db"
    database_path.touch()
    service = CuhkDictionaryService(
        database_path=database_path,
        scraper_kwargs={"cache_dir_path": tmp_path / "cache"},
    )

    with patch.object(service.scraper, "scrape") as mock_scrape:
        with patch.object(service.database, "persist") as mock_persist:
            output = service.build(overwrite=False, max_words=7)

    assert output == database_path
    mock_scrape.assert_not_called()
    mock_persist.assert_not_called()
