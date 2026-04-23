#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.dictionaries.wiktionary.WiktionaryDictionaryParser."""

from __future__ import annotations

import json
from collections.abc import Generator
from pathlib import Path

import pytest

from scinoephile.common.file import get_temp_file_path
from scinoephile.dictionaries.wiktionary.parser import WiktionaryDictionaryParser


@pytest.fixture
def source_jsonl_path() -> Generator[Path]:
    """Provide a temporary Kaikki JSONL source path."""
    with get_temp_file_path(".jsonl") as temp_path:
        yield temp_path


def test_parse_uses_pronunciation_fallback_when_sounds_missing(source_jsonl_path: Path):
    """Generate best-effort pinyin and Jyutping when sounds are absent.

    Arguments:
        source_jsonl_path: temporary Kaikki JSONL source path
    """
    source_jsonl_path.write_text(
        json.dumps(
            {
                "word": "學生",
                "pos": "noun",
                "senses": [{"glosses": ["student"]}],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    _, entries = WiktionaryDictionaryParser().parse(source_jsonl_path=source_jsonl_path)

    assert len(entries) == 1
    entry = entries[0]
    assert entry.traditional == "學生"
    assert entry.simplified == "学生"
    assert entry.pinyin == "xue2 sheng1"
    assert entry.jyutping


def test_parse_deduplicates_duplicate_glosses(source_jsonl_path: Path):
    """Deduplicate repeated glosses while retaining synonym and antonym text.

    Arguments:
        source_jsonl_path: temporary Kaikki JSONL source path
    """
    source_jsonl_path.write_text(
        json.dumps(
            {
                "word": "芒",
                "pos": "noun",
                "sounds": [
                    {
                        "tags": ["Mandarin", "Pinyin", "standard"],
                        "zh-pron": "máng",
                    },
                    {
                        "tags": ["Cantonese", "Guangzhou", "Jyutping"],
                        "zh-pron": "mong⁴",
                    },
                ],
                "senses": [
                    {
                        "glosses": ["awn"],
                        "tags": ["literary"],
                        "synonyms": [{"word": "麥芒"}],
                        "antonyms": [{"word": "光滑"}],
                    },
                    {
                        "glosses": ["awn"],
                        "tags": ["literary"],
                        "synonyms": [{"word": "麥芒"}],
                        "antonyms": [{"word": "光滑"}],
                    },
                ],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    _, entries = WiktionaryDictionaryParser().parse(source_jsonl_path=source_jsonl_path)

    assert len(entries) == 1
    definitions = entries[0].definitions
    assert len(definitions) == 1
    assert definitions[0].label == "noun, literary"
    assert definitions[0].text == "awn\n(syn.) 麥芒\n(ant.) 光滑"


def test_parse_supports_mixed_cantonese_and_mandarin_pronunciations(
    source_jsonl_path: Path,
):
    """Create entries for records with one Jyutping and multiple Mandarin readings.

    Arguments:
        source_jsonl_path: temporary Kaikki JSONL source path
    """
    source_jsonl_path.write_text(
        json.dumps(
            {
                "word": "行",
                "pos": "verb",
                "sounds": [
                    {
                        "tags": ["Mandarin", "Pinyin", "standard"],
                        "zh-pron": "háng",
                    },
                    {
                        "tags": [
                            "Mandarin",
                            "Pinyin",
                            "standard",
                            "toneless-final-syllable-variant",
                        ],
                        "zh-pron": "xíng",
                    },
                    {
                        "tags": ["Cantonese", "Guangzhou", "Jyutping"],
                        "zh-pron": "ha⁴ng",
                    },
                ],
                "senses": [{"glosses": ["to go"]}],
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    _, entries = WiktionaryDictionaryParser().parse(source_jsonl_path=source_jsonl_path)

    assert len(entries) == 2
    assert sorted(entry.pinyin for entry in entries) == ["hang2", "xing2"]
    assert all(entry.jyutping == "hang4" for entry in entries)
