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
from scinoephile.multilang.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
)

from .constants import GZZJ_SOURCE

__all__ = [
    "GzzjDictionaryParser",
]

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

    def _get_definitions(
        self,
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
        if not definitions:
            definitions.append(DictionaryDefinition(text="-"))
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

    def _parse_record(self, record: dict[str, Any]) -> list[DictionaryEntry]:
        """Parse one raw GZZJ record.

        Arguments:
            record: raw JSON record
        Returns:
            normalized dictionary entries
        """
        traditional = unicodedata.normalize("NFKD", str(record["字頭"]))
        extra_data = record.get("_校訂補充")
        raw_variants = (
            extra_data.get("異體", []) if isinstance(extra_data, dict) else []
        )
        variants = [
            unicodedata.normalize("NFKD", str(variant))
            for variant in raw_variants
            if str(variant).strip()
        ]
        headwords = [traditional, *variants]

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
        entries = [
            DictionaryEntry(
                traditional=headword,
                simplified=self.opencc_converter.convert(headword),
                pinyin=self._get_pinyin(self.opencc_converter.convert(headword)),
                jyutping=jyutping,
                frequency=0.0,
                definitions=self._dedupe_definitions(definitions),
            )
            for (headword, jyutping), definitions in definitions_by_key.items()
        ]
        if not entries:
            logger.warning(f"Skipping GZZJ record without readings: {traditional!r}")
        return entries

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
