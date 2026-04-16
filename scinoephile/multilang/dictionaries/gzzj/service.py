#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""GZZJ dictionary service."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.validation import val_input_path, val_int, val_output_path
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings
from scinoephile.lang.id import LanguageIDResult
from scinoephile.lang.yue.romanization import get_yue_jyutping_query_strings
from scinoephile.multilang.dictionaries import DictionaryEntry, DictionarySqliteStore

from .constants import GZZJ_DOWNLOAD_URL, MAX_LOOKUP_LIMIT
from .parser import GzzjDictionaryParser

__all__ = ["GzzjDictionaryService"]


class GzzjDictionaryService:
    """Runtime service for querying locally cached GZZJ dictionary data."""

    def __init__(
        self,
        database_path: Path | None = None,
        *,
        source_json_path: Path | None = None,
        auto_build_missing: bool = False,
    ):
        """Initialize.

        Arguments:
            database_path: SQLite database path
            source_json_path: path to a manually downloaded `B01_資料.json` file
            auto_build_missing: build GZZJ data automatically if missing
        """
        if database_path is None:
            database_path = (
                get_runtime_cache_dir_path("dictionaries", "gzzj") / "gzzj.db"
            )
        if source_json_path is None:
            source_json_path = (
                get_runtime_cache_dir_path("dictionaries", "gzzj") / "B01_資料.json"
            )
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.source_json_path = Path(source_json_path)
        self.auto_build_missing = auto_build_missing
        self.database = DictionarySqliteStore(database_path=self.database_path)
        self.parser = GzzjDictionaryParser()

    def build(self, overwrite: bool = False) -> Path:
        """Build or rebuild the local GZZJ SQLite dictionary.

        Arguments:
            overwrite: whether to overwrite an existing SQLite database
        Returns:
            SQLite database path
        """
        if self.database_path.exists() and not overwrite:
            return self.database_path

        source_json_path = self._require_source_json_path()
        parsed_data = self.parser.parse(source_json_path=source_json_path)
        return self.database.persist(parsed_data)

    def lookup(self, query: str, limit: int = 10) -> list[DictionaryEntry]:
        """Query local GZZJ dictionary data using inferred query formats.

        Arguments:
            query: input text to search
            limit: max results to return
        Returns:
            dictionary entries
        """
        query = query.strip()
        if not query:
            return []
        limit = val_int(limit, min_value=1, max_value=MAX_LOOKUP_LIMIT)

        self._ensure_database()

        query_id = LanguageIDResult(query)
        matched_format = False
        entries: list[DictionaryEntry] = []

        if query_id.is_simplified:
            matched_format = True
            entries.extend(self.database.lookup_by_simplified(query, limit))
        if query_id.is_traditional:
            matched_format = True
            entries.extend(self.database.lookup_by_traditional(query, limit))
        if query_id.is_numbered_pinyin or query_id.is_accented_pinyin:
            matched_format = True
            for pinyin_query in get_cmn_pinyin_query_strings(query):
                entries.extend(self.database.lookup_by_pinyin(pinyin_query, limit))
        if query_id.is_numbered_jyutping or query_id.is_accented_yale:
            matched_format = True
            for jyutping_query in get_yue_jyutping_query_strings(query):
                entries.extend(self.database.lookup_by_jyutping(jyutping_query, limit))

        if matched_format:
            entries_by_key = {
                (
                    entry.traditional,
                    entry.simplified,
                    entry.pinyin,
                    entry.jyutping,
                ): entry
                for entry in entries
            }
            return list(entries_by_key.values())
        raise ValueError(
            f"Could not infer a supported lookup format for query {query!r}"
        )

    def _ensure_database(self):
        """Ensure the SQLite database exists, building it if configured."""
        if self.database_path.exists():
            return
        if not self.auto_build_missing:
            raise FileNotFoundError(
                "GZZJ dictionary database not found. "
                "Set auto_build_missing=True to build automatically, "
                "or build explicitly with GzzjDictionaryService.build()."
            )
        self.build(overwrite=False)

    def _require_source_json_path(self) -> Path:
        """Validate that the manual GZZJ source file is available.

        Returns:
            validated source JSON path
        """
        try:
            return val_input_path(self.source_json_path)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "GZZJ source JSON not found. Download `B01_資料.json` from "
                f"{GZZJ_DOWNLOAD_URL} and pass it with --source-json-path."
            ) from exc
