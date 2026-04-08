#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.multilang.cmn_yue.dictionary_tools."""

from __future__ import annotations

from contextlib import ExitStack
from pathlib import Path

from scinoephile.common.file import get_temp_file_path
from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
    DictionarySqliteStore,
    LookupDirection,
)
from scinoephile.multilang.cmn_yue.dictionary_tools import lookup_dictionary


def _build_dictionary_database(
    database_path: Path,
    *,
    source_name: str,
    source_shortname: str,
    definition_text: str,
):
    """Build a synthetic dictionary SQLite database for tool tests.

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


def test_lookup_dictionary_returns_source_tagged_payload():
    """Test generic dictionary lookup returns source-tagged serialized results."""
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
        payload = lookup_dictionary(
            query="山坑",
            direction=LookupDirection.YUE_TO_CMN.value,
            limit=10,
            database_paths=[database_one_path, database_two_path],
            sources=["synb"],
        )

        assert payload["query"] == "山坑"
        assert payload["direction"] == LookupDirection.YUE_TO_CMN.value
        assert payload["sources"] == ["synb"]
        assert payload["result_count"] == 1
        assert payload["entries"] == [
            {
                "source": {
                    "id": "synb",
                    "shortname": "SYNB",
                    "name": "Synthetic Source Two",
                },
                "traditional": "山坑",
                "simplified": "山坑",
                "pinyin": "shan1 keng1",
                "jyutping": "saan1 haang1",
                "frequency": 5.0,
                "definitions": [
                    {
                        "label": "釋義",
                        "text": "synthetic definition two",
                    }
                ],
            }
        ]
