#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Parse Kaikki Wiktionary JSONL into normalized dictionary entries."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import opencc
import pycantonese
from pypinyin import Style, lazy_pinyin
from pypinyin.contrib.tone_convert import tone_to_tone3

from scinoephile.common.validation import val_input_path
from scinoephile.core.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
)

from .constants import WIKTIONARY_SOURCE

__all__ = ["WiktionaryDictionaryParser"]

JYUTPING_COLLOQUIAL_PRONUNCIATION = re.compile(r".⁻(.)")
JYUTPING_NONSTANDARD_TONE_POSITION = re.compile(r"^([a-z]+?)([1-6])([a-z]+)$")
SUPERSCRIPT_EQUIVALENT = str.maketrans("¹²³⁴⁵⁶⁷⁸⁹⁰", "1234567890")

MANDARIN_PINYIN_TAGS: tuple[tuple[str, ...], ...] = (
    ("Mandarin", "Pinyin", "standard"),
    ("Mandarin", "Pinyin", "standard", "toneless-final-syllable-variant"),
)

CANTONESE_JYUTPING_TAGS: tuple[tuple[str, ...], ...] = (
    ("Cantonese", "Guangzhou", "Jyutping"),
)


class WiktionaryDictionaryParser:
    """Parser for Kaikki Chinese Wiktionary JSONL dumps."""

    def __init__(self):
        """Initialize."""
        self.opencc_converter = opencc.OpenCC("hk2s")

    def parse(
        self, source_jsonl_path: Path
    ) -> tuple[DictionarySource, list[DictionaryEntry]]:
        """Parse Kaikki JSONL dump into dictionary entries.

        Arguments:
            source_jsonl_path: path to Kaikki `wiktionary.json` JSONL dump
        Returns:
            source metadata and normalized dictionary entries
        """
        source_jsonl_path = val_input_path(source_jsonl_path)
        definitions_by_key: dict[
            tuple[str, str, str, str], list[DictionaryDefinition]
        ] = defaultdict(list)

        with source_jsonl_path.open("r", encoding="utf-8") as infile:
            for raw_line in infile:
                line = raw_line.strip()
                if not line:
                    continue
                record = json.loads(line)
                self._append_record_entries(
                    record=record,
                    definitions_by_key=definitions_by_key,
                )

        entries: list[DictionaryEntry] = []
        for (traditional, simplified, pinyin, jyutping), definitions in sorted(
            definitions_by_key.items()
        ):
            entries.append(
                DictionaryEntry(
                    traditional=traditional,
                    simplified=simplified,
                    pinyin=pinyin,
                    jyutping=jyutping,
                    frequency=0.0,
                    definitions=self._dedupe_definitions(definitions),
                )
            )
        return WIKTIONARY_SOURCE, entries

    @staticmethod
    def _dedupe_definitions(
        definitions: list[DictionaryDefinition],
    ) -> list[DictionaryDefinition]:
        """Deduplicate definitions while preserving order.

        Arguments:
            definitions: raw definition list
        Returns:
            deduplicated definitions
        """
        seen: set[tuple[str, str]] = set()
        deduped: list[DictionaryDefinition] = []
        for definition in definitions:
            key = (definition.text, definition.label)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(definition)
        return deduped

    @classmethod
    def _extract_definitions(cls, record: dict[str, Any]) -> list[DictionaryDefinition]:
        """Extract first-pass dictionary definitions from one Kaikki record.

        Arguments:
            record: Kaikki JSON object
        Returns:
            dictionary definitions
        """
        definitions: list[DictionaryDefinition] = []
        part_of_speech = str(record.get("pos", "")).strip()
        for sense in record.get("senses", []):
            if not isinstance(sense, dict):
                continue
            glosses = sense.get("glosses", [])
            if not isinstance(glosses, list) or not glosses:
                continue
            gloss = str(glosses[0]).split("\n", maxsplit=1)[0].strip()
            if not gloss:
                continue
            synonyms = cls._extract_relation_words(sense.get("synonyms"))
            antonyms = cls._extract_relation_words(sense.get("antonyms"))
            definition_text = gloss
            if synonyms:
                definition_text += f"\n(syn.) {', '.join(synonyms)}"
            if antonyms:
                definition_text += f"\n(ant.) {', '.join(antonyms)}"

            tags = [
                str(tag).strip() for tag in sense.get("tags", []) if str(tag).strip()
            ]
            label_parts = [part_of_speech, *tags]
            label = ", ".join(part for part in label_parts if part)
            definitions.append(DictionaryDefinition(text=definition_text, label=label))
        return definitions

    @staticmethod
    def _extract_relation_words(value: Any) -> list[str]:
        """Extract related words from a Kaikki relation list.

        Arguments:
            value: relation payload such as `synonyms` or `antonyms`
        Returns:
            related words
        """
        if not isinstance(value, list):
            return []
        words: list[str] = []
        for item in value:
            if not isinstance(item, dict):
                continue
            word = str(item.get("word", "")).replace(" (", "").strip()
            if not word or "／" in word:
                continue
            words.append(word)
        return words

    def _append_record_entries(
        self,
        *,
        record: dict[str, Any],
        definitions_by_key: dict[tuple[str, str, str, str], list[DictionaryDefinition]],
    ):
        """Append parsed record data into the aggregate entry map.

        Arguments:
            record: Kaikki JSON object
            definitions_by_key: aggregate definitions keyed by entry identity
        """
        traditional = str(record.get("word", "")).strip()
        if not traditional:
            return
        simplified = self.opencc_converter.convert(traditional)

        pinyin_values = self._extract_pinyin_values(record)
        if not pinyin_values:
            pinyin_values = [self._fallback_pinyin(traditional)]
        jyutping_values = self._extract_jyutping_values(record)
        if not jyutping_values:
            fallback_jyutping = self._fallback_jyutping(traditional)
            if fallback_jyutping:
                jyutping_values = [fallback_jyutping]
        if not jyutping_values:
            jyutping_values = [""]

        definitions = self._extract_definitions(record)
        for pinyin in pinyin_values:
            for jyutping in jyutping_values:
                key = (traditional, simplified, pinyin, jyutping)
                definitions_by_key[key].extend(definitions)

    @classmethod
    def _extract_jyutping_values(cls, record: dict[str, Any]) -> list[str]:
        """Extract explicit Cantonese Jyutping from Kaikki sound records.

        Arguments:
            record: Kaikki JSON object
        Returns:
            normalized Jyutping values
        """
        values: list[str] = []
        for sound in record.get("sounds", []):
            if not isinstance(sound, dict):
                continue
            tags = tuple(sound.get("tags", []))
            if tags not in CANTONESE_JYUTPING_TAGS:
                continue
            romanization = cls._get_sound_romanization(sound)
            normalized = cls._normalize_jyutping(romanization)
            if normalized and normalized not in values:
                values.append(normalized)
        return values

    @classmethod
    def _extract_pinyin_values(cls, record: dict[str, Any]) -> list[str]:
        """Extract explicit Mandarin pinyin from Kaikki sound records.

        Arguments:
            record: Kaikki JSON object
        Returns:
            normalized numbered pinyin values
        """
        values: list[str] = []
        for sound in record.get("sounds", []):
            if not isinstance(sound, dict):
                continue
            tags = tuple(sound.get("tags", []))
            if tags not in MANDARIN_PINYIN_TAGS:
                continue
            romanization = cls._get_sound_romanization(sound)
            normalized = cls._normalize_pinyin(romanization)
            if normalized and normalized not in values:
                values.append(normalized)
        return values

    @staticmethod
    def _get_sound_romanization(sound: dict[str, Any]) -> str:
        """Get one pronunciation value from a Kaikki sound record.

        Arguments:
            sound: Kaikki sound record
        Returns:
            pronunciation string
        """
        if "zh_pron" in sound:
            return str(sound.get("zh_pron", "")).strip()
        return str(sound.get("zh-pron", "")).strip()

    @staticmethod
    def _fallback_jyutping(text: str) -> str:
        """Generate best-effort Jyutping when Wiktionary data omits it.

        Arguments:
            text: headword text
        Returns:
            Jyutping text, or an empty string if no mapping exists
        """
        romanization_items = pycantonese.characters_to_jyutping([text])
        if not romanization_items:
            return ""
        _, jyutping = romanization_items[0]
        if jyutping is None:
            return ""
        return jyutping.lower().strip()

    @staticmethod
    def _fallback_pinyin(text: str) -> str:
        """Generate numbered pinyin from Hanzi when Wiktionary omits it.

        Arguments:
            text: headword text
        Returns:
            numbered pinyin
        """
        return (
            " ".join(
                lazy_pinyin(
                    text,
                    style=Style.TONE3,
                    neutral_tone_with_five=True,
                    v_to_u=True,
                )
            )
            .lower()
            .replace("ü", "u:")
            .strip()
        )

    @staticmethod
    def _normalize_jyutping(text: str) -> str:
        """Normalize Kaikki Jyutping-like strings to numbered Jyutping.

        Arguments:
            text: Kaikki Jyutping string
        Returns:
            normalized Jyutping
        """
        normalized = text.translate(SUPERSCRIPT_EQUIVALENT).strip().lower()
        if not normalized:
            return ""

        tokens: list[str] = []
        for raw_token in normalized.split():
            normalized_token = JYUTPING_COLLOQUIAL_PRONUNCIATION.sub(r"\1", raw_token)
            match = JYUTPING_NONSTANDARD_TONE_POSITION.match(normalized_token)
            if match:
                normalized_token = f"{match.group(1)}{match.group(3)}{match.group(2)}"
            tokens.append(normalized_token)
        return " ".join(tokens)

    @staticmethod
    def _normalize_pinyin(text: str) -> str:
        """Normalize Kaikki pinyin strings to numbered pinyin.

        Arguments:
            text: Kaikki pinyin string
        Returns:
            normalized numbered pinyin
        """
        if not text:
            return ""
        normalized_tokens: list[str] = []
        for token in text.replace("'", " ").split():
            lowered = token.lower()
            try:
                normalized = tone_to_tone3(lowered).lower().replace("ü", "u:")
            except ValueError:
                normalized = lowered.replace("ü", "u:")
            if normalized:
                normalized_tokens.append(normalized)
        return " ".join(normalized_tokens)
