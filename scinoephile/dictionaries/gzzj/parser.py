#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""GZZJ dictionary parsing from manually downloaded JSON data."""

from __future__ import annotations

import json
import unicodedata
from logging import getLogger
from pathlib import Path
from typing import Any

import opencc
from pypinyin import Style, lazy_pinyin

from scinoephile.common.validation import val_input_path
from scinoephile.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
)

from .constants import GZZJ_SOURCE

__all__ = ["GzzjDictionaryParser"]

logger = getLogger(__name__)

NUMERICAL_VALUES = str.maketrans("①②③④⑤⑥⑦⑧⑨⑩", "\n\n\n\n\n\n\n\n\n\n", "㈠㈡㈢㈣")


class GzzjDictionaryParser:
    """Parser for GZZJ dictionary source JSON."""

    def __init__(self):
        """Initialize."""
        self.opencc_converter = opencc.OpenCC("hk2s")

    def parse(
        self,
        source_json_path: Path,
    ) -> tuple[DictionarySource, list[DictionaryEntry]]:
        """Parse a manually downloaded GZZJ source file.

        Arguments:
            source_json_path: path to `B01_資料.json`
        Returns:
            source metadata and normalized dictionary entries
        """
        source_json_path = val_input_path(source_json_path)
        data = json.loads(source_json_path.read_text(encoding="utf-8"))

        entries: list[DictionaryEntry] = []
        for record in data:
            entries.extend(self._parse_record(record))

        return GZZJ_SOURCE, entries

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
    def _get_definitions(
        *,
        explanation: str | None,
        variants: list[str],
        marker: str | None,
        note: str | None,
    ) -> list[DictionaryDefinition]:
        """Build normalized definitions for one reading.

        Arguments:
            explanation: optional raw explanation text
            variants: alternate headword forms
            marker: reading marker such as `又`
            note: optional editor note
        Returns:
            normalized definitions
        """
        definitions: list[DictionaryDefinition] = []
        if explanation:
            normalized_explanation = explanation.translate(NUMERICAL_VALUES)
            definitions.extend(
                DictionaryDefinition(text=definition_text, label="釋義")
                for definition_text in normalized_explanation.split()
            )
        if variants:
            definitions.append(
                DictionaryDefinition(text="|".join(variants), label="異體")
            )
        if marker:
            definitions.append(DictionaryDefinition(text=marker, label="讀音標記"))
        if note:
            definitions.append(DictionaryDefinition(text=note, label="校訂註"))
        return definitions

    @staticmethod
    def _get_pinyin(text: str) -> str:
        """Get numbered pinyin for a headword.

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
        )

    @staticmethod
    def _normalize_text_values(value: Any) -> list[str]:
        """Normalize one or more text values into a flat string list.

        Arguments:
            value: scalar or list-like text value
        Returns:
            normalized non-empty text values
        """
        if isinstance(value, list):
            raw_values = value
        else:
            raw_values = [value]

        normalized_values: list[str] = []
        for raw_value in raw_values:
            normalized_value = unicodedata.normalize("NFKD", str(raw_value)).strip()
            if normalized_value:
                normalized_values.append(normalized_value)
        return normalized_values

    @classmethod
    def _get_headwords(cls, record: dict[str, Any]) -> list[str]:
        """Get normalized headwords for one record.

        Arguments:
            record: raw JSON record
        Returns:
            normalized headwords and variants in source order
        """
        primary_headwords = cls._normalize_text_values(record["字頭"])
        extra_data = record.get("_校訂補充")
        raw_variants = (
            extra_data.get("異體", []) if isinstance(extra_data, dict) else []
        )
        variants = cls._normalize_text_values(raw_variants)

        seen_headwords: set[str] = set()
        headwords: list[str] = []
        for headword in [*primary_headwords, *variants]:
            if headword in seen_headwords:
                continue
            seen_headwords.add(headword)
            headwords.append(headword)
        return headwords

    @classmethod
    def _get_record_variants(cls, record: dict[str, Any]) -> list[str]:
        """Get normalized variant headwords for one record.

        Arguments:
            record: raw JSON record
        Returns:
            normalized variant headwords
        """
        extra_data = record.get("_校訂補充")
        raw_variants = (
            extra_data.get("異體", []) if isinstance(extra_data, dict) else []
        )
        return cls._normalize_text_values(raw_variants)

    def _parse_record(self, record: dict[str, Any]) -> list[DictionaryEntry]:
        """Parse one raw GZZJ record.

        Arguments:
            record: raw JSON record
        Returns:
            normalized dictionary entries
        """
        headwords = self._get_headwords(record)
        if not headwords:
            logger.warning(f"Skipping GZZJ record without headword: {record!r}")
            return []
        traditional = headwords[0]
        variants = self._get_record_variants(record)

        definitions_by_key: dict[tuple[str, str], list[DictionaryDefinition]] = {}
        raw_senses = record.get("義項", [])
        if not isinstance(raw_senses, list):
            raw_senses = []
        for sense in raw_senses:
            if not isinstance(sense, dict):
                continue
            explanation = sense.get("釋義")
            for reading in sense.get("讀音", []):
                if not isinstance(reading, dict):
                    continue
                jyutping = str(reading.get("粵拼讀音") or "").strip().lower()
                if not jyutping:
                    continue
                marker = str(reading.get("讀音標記") or "").strip()
                note = ""
                extra_data = reading.get("_校訂補充")
                if isinstance(extra_data, dict):
                    note = str(extra_data.get("校訂註") or "").strip()

                definitions = self._get_definitions(
                    explanation=str(explanation).strip() if explanation else None,
                    variants=variants,
                    marker=marker or None,
                    note=note or None,
                )
                for headword in headwords:
                    definitions_by_key.setdefault((headword, jyutping), []).extend(
                        definitions
                    )
        entries: list[DictionaryEntry] = []
        for (headword, jyutping), definitions in definitions_by_key.items():
            simplified = self.opencc_converter.convert(headword)
            entries.append(
                DictionaryEntry(
                    traditional=headword,
                    simplified=simplified,
                    pinyin=self._get_pinyin(simplified),
                    jyutping=jyutping,
                    frequency=0.0,
                    definitions=self._dedupe_definitions(definitions),
                )
            )
        if not entries:
            logger.warning(f"Skipping GZZJ record without readings: {traditional!r}")
        return entries
