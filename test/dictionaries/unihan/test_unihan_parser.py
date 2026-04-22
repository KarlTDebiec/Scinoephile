#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.dictionaries.unihan.UnihanDictionaryParser."""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_directory_path
from scinoephile.dictionaries.unihan.parser import UnihanDictionaryParser


@pytest.fixture
def source_dir_path() -> Generator[Path]:
    """Provide a temporary directory for Unihan source fixtures."""
    with get_temp_directory_path() as dir_path:
        yield dir_path


def _write_unihan_fixture_files(source_dir_path: Path):
    """Write deterministic Unihan source fixture files.

    Arguments:
        source_dir_path: fixture source directory path
    """
    (source_dir_path / "Unihan_Variants.txt").write_text(
        ("U+4E07\tkTraditionalVariant\tU+842C\nU+5B78\tkSimplifiedVariant\tU+5B66\n"),
        encoding="utf-8",
    )
    (source_dir_path / "Unihan_Readings.txt").write_text(
        (
            "U+4E00\tkCantonese\tjat1\n"
            "U+4E00\tkMandarin\tyī\n"
            "U+4E00\tkDefinition\tone;single\n"
            "U+842C\tkCantonese\tmaan6\n"
            "U+842C\tkMandarin\twàn\n"
            "U+842C\tkDefinition\tten thousand\n"
            "U+5B78\tkCantonese\thok6\n"
            "U+5B78\tkMandarin\txué\n"
            "U+5B78\tkDefinition\tstudy\n"
        ),
        encoding="utf-8",
    )
    (source_dir_path / "Unihan_DictionaryLikeData.txt").write_text(
        (
            "U+4E00\tkCangjie\tM\n"
            "U+842C\tkCangjie\tDQ\n"
            "U+5B78\tkCangjie\tYKD\n"
            "U+5B66\tkCangjie\tYKD\n"
        ),
        encoding="utf-8",
    )


def test_parse_variants_readings_and_dictionary_like_data(source_dir_path: Path):
    """Parse representative Unihan inputs into normalized dictionary entries.

    Arguments:
        source_dir_path: fixture source directory path
    """
    _write_unihan_fixture_files(source_dir_path)
    parser = UnihanDictionaryParser()

    _, entries = parser.parse(
        dictionary_like_data_path=source_dir_path / "Unihan_DictionaryLikeData.txt",
        readings_path=source_dir_path / "Unihan_Readings.txt",
        variants_path=source_dir_path / "Unihan_Variants.txt",
    )
    entries_by_key = {
        (entry.traditional, entry.simplified, entry.pinyin, entry.jyutping): entry
        for entry in entries
    }

    assert ("一", "一", "yi1", "jat1") in entries_by_key
    one_entry = entries_by_key[("一", "一", "yi1", "jat1")]
    assert [
        definition.text
        for definition in one_entry.definitions
        if definition.label == "釋義"
    ] == [
        "one",
        "single",
    ]

    assert ("萬", "万", "wan4", "maan6") in entries_by_key
    variant_entry = entries_by_key[("萬", "万", "wan4", "maan6")]
    assert any(
        definition.label == "Cangjie Input - Traditional" and definition.text == "DQ"
        for definition in variant_entry.definitions
    )

    assert ("學", "学", "xue2", "hok6") in entries_by_key
    paired_entry = entries_by_key[("學", "学", "xue2", "hok6")]
    assert any(
        definition.label == "Cangjie Input" and definition.text == "YKD"
        for definition in paired_entry.definitions
    )


def test_parse_readings_preserves_simplified_only_source_rows(source_dir_path: Path):
    """Preserve readings that exist only on the simplified side of a variant pair.

    Arguments:
        source_dir_path: fixture source directory path
    """
    (source_dir_path / "Unihan_Variants.txt").write_text(
        "U+4E07\tkTraditionalVariant\tU+842C\n",
        encoding="utf-8",
    )
    (source_dir_path / "Unihan_Readings.txt").write_text(
        (
            "U+4E07\tkMandarin\twan\n"
            "U+4E07\tkCantonese\tmaan6\n"
            "U+4E07\tkDefinition\tten thousand\n"
        ),
        encoding="utf-8",
    )
    (source_dir_path / "Unihan_DictionaryLikeData.txt").write_text(
        "",
        encoding="utf-8",
    )

    _, entries = UnihanDictionaryParser().parse(
        dictionary_like_data_path=source_dir_path / "Unihan_DictionaryLikeData.txt",
        readings_path=source_dir_path / "Unihan_Readings.txt",
        variants_path=source_dir_path / "Unihan_Variants.txt",
    )

    assert len(entries) == 1
    entry = entries[0]
    assert entry.traditional == "萬"
    assert entry.simplified == "万"
    assert entry.pinyin == "wan"
    assert entry.jyutping == "maan6"
    assert [definition.text for definition in entry.definitions] == ["ten thousand"]
