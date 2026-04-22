#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Parse canonical Kaifangcidian CSV into normalized dictionary entries."""

from __future__ import annotations

import csv
from pathlib import Path

from scinoephile.common.validation import val_input_path
from scinoephile.dictionaries import (
    DictionaryDefinition,
    DictionaryEntry,
    DictionarySource,
)

from .constants import KAIFANGCIDIAN_SOURCE

__all__ = ["KaifangcidianDictionaryParser"]


class KaifangcidianDictionaryParser:
    """Parser for canonical Kaifangcidian CSV data."""

    def parse(
        self, source_csv_path: Path
    ) -> tuple[DictionarySource, list[DictionaryEntry]]:
        """Parse canonical Kaifangcidian CSV data.

        Arguments:
            source_csv_path: canonical CSV path
        Returns:
            source metadata and normalized dictionary entries
        """
        source_csv_path = val_input_path(source_csv_path)
        rows = self._read_rows(source_csv_path)
        entries = self._rows_to_entries(rows)
        return KAIFANGCIDIAN_SOURCE, entries

    @staticmethod
    def _read_rows(source_csv_path: Path) -> list[dict[str, str]]:
        """Read canonical Kaifangcidian CSV rows.

        Arguments:
            source_csv_path: canonical CSV path
        Returns:
            CSV rows
        """
        with source_csv_path.open("r", encoding="utf-8", newline="") as infile:
            return [dict(row) for row in csv.DictReader(infile)]

    @staticmethod
    def _rows_to_entries(rows: list[dict[str, str]]) -> list[DictionaryEntry]:
        """Convert canonical CSV rows into dictionary entries.

        Arguments:
            rows: canonical CSV rows
        Returns:
            dictionary entries
        """
        definitions_by_key: dict[
            tuple[str, str, str, str],
            list[DictionaryDefinition],
        ] = {}
        for row in rows:
            traditional = row.get("traditional", "").strip()
            simplified = row.get("simplified", "").strip()
            pinyin = row.get("pinyin", "").strip()
            jyutping = row.get("jyutping", "").strip().lower()
            if not traditional:
                continue
            key = (
                traditional,
                simplified or traditional,
                pinyin,
                jyutping,
            )
            definitions_by_key.setdefault(key, [])
            definitions_by_key[key].extend(
                KaifangcidianDictionaryParser._row_definitions(row)
            )

        entries: list[DictionaryEntry] = []
        for key, definitions in sorted(definitions_by_key.items()):
            traditional, simplified, pinyin, jyutping = key
            entries.append(
                DictionaryEntry(
                    traditional=traditional,
                    simplified=simplified,
                    pinyin=pinyin,
                    jyutping=jyutping,
                    frequency=0.0,
                    definitions=KaifangcidianDictionaryParser._dedupe_definitions(
                        definitions
                    ),
                )
            )
        return entries

    @staticmethod
    def _row_definitions(row: dict[str, str]) -> list[DictionaryDefinition]:
        """Get normalized definitions for one canonical CSV row.

        Arguments:
            row: canonical CSV row
        Returns:
            dictionary definitions
        """
        definitions: list[DictionaryDefinition] = []
        definition_text = row.get("definition", "").strip()
        note_text = row.get("note", "").strip()
        variants_text = row.get("variants", "").strip()
        kind_text = row.get("kind", "").strip()

        if definition_text:
            definitions.append(DictionaryDefinition(text=definition_text, label="釋義"))
        if note_text:
            definitions.append(DictionaryDefinition(text=note_text, label="註記"))
        if variants_text:
            definitions.append(DictionaryDefinition(text=variants_text, label="異體"))
        if kind_text:
            definitions.append(DictionaryDefinition(text=kind_text, label="來源"))
        if definitions:
            return definitions
        return [DictionaryDefinition(text="（沒有對應漢語詞彙）", label="釋義")]

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
