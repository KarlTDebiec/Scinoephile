#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Unihan dictionary parsing from downloaded text files."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path

from pypinyin.contrib.tone_convert import tone_to_tone3

from scinoephile.common.validation import val_input_path
from scinoephile.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
)

from .constants import UNIHAN_SOURCE

__all__ = ["UnihanDictionaryParser"]

logger = getLogger(__name__)


@dataclass
class _EntryData:
    """Mutable accumulator for one traditional/simplified pair."""

    pinyin_values: set[str] = field(default_factory=set)
    """Mandarin pinyin values."""

    jyutping_values: set[str] = field(default_factory=set)
    """Cantonese Jyutping values."""

    definitions: list[DictionaryDefinition] = field(default_factory=list)
    """Definition metadata rows."""


class UnihanDictionaryParser:
    """Parser for Unihan variant, reading, and dictionary-like files."""

    def parse(
        self,
        *,
        dictionary_like_data_path: Path,
        readings_path: Path,
        variants_path: Path,
    ) -> tuple[DictionarySource, list[DictionaryEntry]]:
        """Parse Unihan source files.

        Arguments:
            dictionary_like_data_path: path to `Unihan_DictionaryLikeData.txt`
            readings_path: path to `Unihan_Readings.txt`
            variants_path: path to `Unihan_Variants.txt`
        Returns:
            source metadata and normalized dictionary entries
        """
        dictionary_like_data_path = val_input_path(dictionary_like_data_path)
        readings_path = val_input_path(readings_path)
        variants_path = val_input_path(variants_path)

        pairs = self._parse_variants(variants_path)
        traditional_index, simplified_index = self._build_variant_indices(pairs)
        entries_data: dict[tuple[str, str], _EntryData] = {
            pair: _EntryData() for pair in pairs
        }

        self._parse_readings(
            readings_path=readings_path,
            entries_data=entries_data,
            traditional_index=traditional_index,
            simplified_index=simplified_index,
        )
        self._parse_dictionary_like_data(
            dictionary_like_data_path=dictionary_like_data_path,
            entries_data=entries_data,
            traditional_index=traditional_index,
            simplified_index=simplified_index,
        )

        entries = self._entries_data_to_entries(entries_data)
        return UNIHAN_SOURCE, entries

    @classmethod
    def _append_cangjie(
        cls,
        *,
        entry_data: _EntryData,
        label: str,
        content: str,
    ):
        """Append Cangjie metadata with merge logic for trad/simp duplicates.

        Arguments:
            entry_data: mutable entry accumulator
            label: cangjie label to append
            content: cangjie content text
        """
        if label == "Cangjie Input":
            entry_data.definitions.append(
                DictionaryDefinition(text=content, label=label)
            )
            return

        for index, definition in enumerate(entry_data.definitions):
            if (
                definition.label.startswith("Cangjie Input -")
                and definition.text == content
            ):
                entry_data.definitions[index] = DictionaryDefinition(
                    text=content, label="Cangjie Input"
                )
                return

        entry_data.definitions.append(DictionaryDefinition(text=content, label=label))

    @classmethod
    def _entries_data_to_entries(
        cls,
        entries_data: dict[tuple[str, str], _EntryData],
    ) -> list[DictionaryEntry]:
        """Convert mutable accumulators into normalized dictionary entries.

        Arguments:
            entries_data: mutable entry accumulators
        Returns:
            normalized dictionary entries
        """
        entries: list[DictionaryEntry] = []
        for (traditional, simplified), entry_data in sorted(entries_data.items()):
            definitions = cls._dedupe_definitions(entry_data.definitions)
            pinyin_values = sorted(entry_data.pinyin_values) or [""]
            jyutping_values = sorted(entry_data.jyutping_values) or [""]
            entries.extend(
                DictionaryEntry(
                    traditional=traditional,
                    simplified=simplified,
                    pinyin=pinyin,
                    jyutping=jyutping,
                    frequency=0.0,
                    definitions=definitions,
                )
                for pinyin in pinyin_values
                for jyutping in jyutping_values
            )
        return entries

    @classmethod
    def _entry_pairs_for_character(
        cls,
        *,
        character: str,
        entries_data: dict[tuple[str, str], _EntryData],
        traditional_index: dict[str, set[tuple[str, str]]],
        simplified_index: dict[str, set[tuple[str, str]]],
    ) -> tuple[list[tuple[str, str]], bool]:
        """Get pairs affected by one character with upstream-compatible behavior.

        Arguments:
            character: normalized character
            entries_data: mutable entry accumulators
            traditional_index: index of variant pairs by traditional form
            simplified_index: index of variant pairs by simplified form
        Returns:
            affected pairs and whether the character appears as simplified
        """
        if character in traditional_index:
            return sorted(traditional_index[character]), character in simplified_index
        if character in simplified_index:
            return [], True
        pair = (character, character)
        entries_data.setdefault(pair, _EntryData())
        traditional_index.setdefault(character, set()).add(pair)
        simplified_index.setdefault(character, set()).add(pair)
        return [pair], False

    @classmethod
    def _parse_dictionary_like_data(
        cls,
        *,
        dictionary_like_data_path: Path,
        entries_data: dict[tuple[str, str], _EntryData],
        traditional_index: dict[str, set[tuple[str, str]]],
        simplified_index: dict[str, set[tuple[str, str]]],
    ):
        """Parse dictionary-like metadata into entry accumulators.

        Arguments:
            dictionary_like_data_path: path to `Unihan_DictionaryLikeData.txt`
            entries_data: mutable entry accumulators
            traditional_index: index of variant pairs by traditional form
            simplified_index: index of variant pairs by simplified form
        """
        for codepoint, field_name, content in cls._parse_unihan_rows(
            dictionary_like_data_path
        ):
            if field_name != "kCangjie":
                continue
            character = cls._parse_character(codepoint)
            if character is None:
                continue

            trad_pairs = sorted(traditional_index.get(character, set()))
            simp_pairs = sorted(simplified_index.get(character, set()))
            if not trad_pairs and not simp_pairs:
                logger.warning(
                    f"Skipping Cangjie for {character!r}: no matching Unihan entry pair"
                )
                continue

            for pair in trad_pairs:
                traditional, simplified = pair
                if traditional == simplified:
                    cls._append_cangjie(
                        entry_data=entries_data[pair],
                        label="Cangjie Input",
                        content=content,
                    )
                else:
                    cls._append_cangjie(
                        entry_data=entries_data[pair],
                        label="Cangjie Input - Traditional",
                        content=content,
                    )
            for pair in simp_pairs:
                traditional, simplified = pair
                if traditional == simplified:
                    continue
                cls._append_cangjie(
                    entry_data=entries_data[pair],
                    label="Cangjie Input - Simplified",
                    content=content,
                )

    @classmethod
    def _parse_readings(
        cls,
        *,
        readings_path: Path,
        entries_data: dict[tuple[str, str], _EntryData],
        traditional_index: dict[str, set[tuple[str, str]]],
        simplified_index: dict[str, set[tuple[str, str]]],
    ):
        """Parse readings/definitions into entry accumulators.

        Arguments:
            readings_path: path to `Unihan_Readings.txt`
            entries_data: mutable entry accumulators
            traditional_index: index of variant pairs by traditional form
            simplified_index: index of variant pairs by simplified form
        """
        for codepoint, field_name, content in cls._parse_unihan_rows(readings_path):
            if field_name not in {"kCantonese", "kMandarin", "kDefinition"}:
                continue
            character = cls._parse_character(codepoint)
            if character is None:
                continue

            pairs, simplified_only = cls._entry_pairs_for_character(
                character=character,
                entries_data=entries_data,
                traditional_index=traditional_index,
                simplified_index=simplified_index,
            )
            if simplified_only and not pairs:
                continue

            for pair in pairs:
                entry_data = entries_data[pair]
                if field_name == "kCantonese":
                    entry_data.jyutping_values.update(cls._normalize_cantonese(content))
                elif field_name == "kMandarin":
                    entry_data.pinyin_values.update(cls._normalize_mandarin(content))
                elif field_name == "kDefinition":
                    entry_data.definitions.extend(
                        DictionaryDefinition(text=text, label="釋義")
                        for text in (segment.strip() for segment in content.split(";"))
                        if text
                    )

    @classmethod
    def _parse_variants(cls, variants_path: Path) -> set[tuple[str, str]]:
        """Parse traditional/simplified variant pairs.

        Arguments:
            variants_path: path to `Unihan_Variants.txt`
        Returns:
            set of `(traditional, simplified)` pairs
        """
        pairs: set[tuple[str, str]] = set()
        for codepoint, field_name, content in cls._parse_unihan_rows(variants_path):
            if field_name not in {"kSimplifiedVariant", "kTraditionalVariant"}:
                continue
            character = cls._parse_character(codepoint)
            if character is None:
                continue
            variants = [
                variant
                for token in content.split()
                if (variant := cls._parse_character(token)) is not None
            ]
            if field_name == "kTraditionalVariant":
                for variant in variants:
                    pairs.add((variant, character))
            else:
                for variant in variants:
                    pairs.add((character, variant))
        return pairs

    @staticmethod
    def _build_variant_indices(
        pairs: set[tuple[str, str]],
    ) -> tuple[dict[str, set[tuple[str, str]]], dict[str, set[tuple[str, str]]]]:
        """Build character-to-pair indices for variant pairs.

        Arguments:
            pairs: `(traditional, simplified)` pairs
        Returns:
            indices by traditional character, and by simplified character
        """
        traditional_index: dict[str, set[tuple[str, str]]] = defaultdict(set)
        simplified_index: dict[str, set[tuple[str, str]]] = defaultdict(set)
        for pair in pairs:
            traditional, simplified = pair
            traditional_index[traditional].add(pair)
            simplified_index[simplified].add(pair)
        return dict(traditional_index), dict(simplified_index)

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

    @staticmethod
    def _normalize_cantonese(content: str) -> list[str]:
        """Normalize Cantonese content into Jyutping tokens.

        Arguments:
            content: Unihan `kCantonese` content value
        Returns:
            normalized Jyutping tokens
        """
        return [token.lower() for token in content.split() if token]

    @staticmethod
    def _normalize_mandarin(content: str) -> list[str]:
        """Normalize accented Mandarin pinyin to numbered pinyin.

        Arguments:
            content: Unihan `kMandarin` content value
        Returns:
            normalized pinyin tokens
        """
        normalized_values: list[str] = []
        for token in content.lower().split():
            if not token:
                continue
            numbered = tone_to_tone3(token).lower().replace("ü", "u:")
            if numbered:
                normalized_values.append(numbered)
        return normalized_values

    @staticmethod
    def _parse_character(codepoint: str) -> str | None:
        """Parse one Unihan codepoint token into a character.

        Arguments:
            codepoint: Unihan codepoint token such as `U+4E00`
        Returns:
            corresponding character, or None if malformed
        """
        if not codepoint.startswith("U+"):
            return None
        try:
            return chr(int(codepoint[2:], 16))
        except ValueError:
            return None

    @staticmethod
    def _parse_unihan_rows(source_path: Path) -> list[tuple[str, str, str]]:
        """Parse non-comment Unihan rows from one file.

        Arguments:
            source_path: Unihan text file path
        Returns:
            parsed `(codepoint, field_name, content)` tuples
        """
        rows: list[tuple[str, str, str]] = []
        for raw_line in source_path.read_text(encoding="utf-8").splitlines():
            if not raw_line or raw_line.startswith("#"):
                continue
            parts = raw_line.split("\t", maxsplit=2)
            if len(parts) != 3:
                continue
            codepoint, field_name, content = (part.strip() for part in parts)
            if not codepoint or not field_name:
                continue
            rows.append((codepoint, field_name, content))
        return rows
