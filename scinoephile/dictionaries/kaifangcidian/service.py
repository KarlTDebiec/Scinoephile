#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Kaifangcidian dictionary service."""

from __future__ import annotations

import shutil
from pathlib import Path

from scinoephile.common.validation import val_input_path, val_int, val_output_path
from scinoephile.core.dictionaries import DictionaryEntry, DictionarySqliteStore
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings
from scinoephile.lang.id import LanguageIDResult
from scinoephile.lang.yue.romanization import get_yue_jyutping_query_strings

from .constants import KAIFANGCIDIAN_LOCAL_CSV_PATH, MAX_LOOKUP_LIMIT
from .downloader import KaifangcidianDownloader
from .parser import KaifangcidianDictionaryParser

__all__ = ["KaifangcidianDictionaryService"]


class KaifangcidianDictionaryService:
    """Runtime service for querying locally cached Kaifangcidian data."""

    def __init__(
        self,
        database_path: Path | None = None,
        *,
        auto_build_missing: bool = False,
        local_data_dir_path: Path | None = None,
        runtime_data_dir_path: Path | None = None,
    ):
        """Initialize.

        Arguments:
            database_path: SQLite database path
            auto_build_missing: build Kaifangcidian data automatically if missing
            local_data_dir_path: optional local canonical data directory override
            runtime_data_dir_path: optional runtime canonical data directory override
        """
        if database_path is None:
            database_path = (
                get_runtime_cache_dir_path("dictionaries", "kaifangcidian")
                / "kaifangcidian.db"
            )
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.auto_build_missing = auto_build_missing
        self.database = DictionarySqliteStore(database_path=self.database_path)
        self.parser = KaifangcidianDictionaryParser()
        self.downloader = KaifangcidianDownloader()

        self.local_data_dir_path = (
            local_data_dir_path
            if local_data_dir_path is not None
            else KAIFANGCIDIAN_LOCAL_CSV_PATH.parent
        )
        self.runtime_data_dir_path = (
            runtime_data_dir_path
            if runtime_data_dir_path is not None
            else get_runtime_cache_dir_path("dictionaries", "kaifangcidian", "data")
        )

    def build(
        self,
        *,
        overwrite: bool = False,
        force_download: bool = False,
        update_local_data: bool = False,
    ) -> Path:
        """Build or rebuild the local Kaifangcidian SQLite dictionary.

        Arguments:
            overwrite: whether to overwrite an existing SQLite database
            force_download: force fresh website download before build
            update_local_data: update canonical local CSV in repository data directory
        Returns:
            sqlite database path
        """
        if self.database_path.exists() and not overwrite:
            return self.database_path

        source_csv_path = self._require_source_csv_path(
            force_download=force_download,
            update_local_data=update_local_data,
        )
        parsed_data = self.parser.parse(source_csv_path=source_csv_path)
        return self.database.persist(parsed_data)

    def lookup(self, query: str, limit: int = 10) -> list[DictionaryEntry]:
        """Query local Kaifangcidian data using inferred query formats.

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
                "Kaifangcidian dictionary database not found. "
                "Set auto_build_missing=True to build automatically, "
                "or build explicitly with KaifangcidianDictionaryService.build()."
            )
        self.build(overwrite=False)

    def _require_source_csv_path(
        self,
        *,
        force_download: bool,
        update_local_data: bool,
    ) -> Path:
        """Get canonical source CSV, downloading and normalizing if needed.

        Arguments:
            force_download: force fresh website download before build
            update_local_data: update canonical local CSV in repository data directory
        Returns:
            canonical source CSV path
        """
        local_csv_path = self.local_data_dir_path / "entries.csv"
        runtime_csv_path = self.runtime_data_dir_path / "entries.csv"

        if not force_download and local_csv_path.exists():
            return val_input_path(local_csv_path)
        if not force_download and runtime_csv_path.exists():
            if update_local_data:
                return self._copy_runtime_csv_to_local(
                    runtime_csv_path=runtime_csv_path,
                    local_csv_path=local_csv_path,
                )
            return val_input_path(runtime_csv_path)

        runtime_csv_path = self.downloader.download_to_csv(runtime_csv_path)
        if not update_local_data:
            return runtime_csv_path

        return self._copy_runtime_csv_to_local(
            runtime_csv_path=runtime_csv_path,
            local_csv_path=local_csv_path,
        )

    def _copy_runtime_csv_to_local(
        self,
        *,
        runtime_csv_path: Path,
        local_csv_path: Path,
    ) -> Path:
        """Copy runtime canonical CSV into the repository-local snapshot.

        Arguments:
            runtime_csv_path: runtime canonical CSV path
            local_csv_path: repository-local canonical CSV path
        Returns:
            local canonical CSV path
        """
        self.local_data_dir_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(runtime_csv_path, local_csv_path)
        return val_input_path(local_csv_path)
