#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Wiktionary dictionary service."""

from __future__ import annotations

import shutil
from pathlib import Path

import requests

from scinoephile.common.validation import val_input_path, val_int, val_output_path
from scinoephile.core.dictionaries import DictionaryEntry, DictionarySqliteStore
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings
from scinoephile.lang.id import LanguageIDResult
from scinoephile.lang.yue.romanization import get_yue_jyutping_query_strings

from .constants import (
    MAX_LOOKUP_LIMIT,
    WIKTIONARY_KAIKKI_JSONL_URL,
    WIKTIONARY_LOCAL_JSONL_PATH,
)
from .parser import WiktionaryDictionaryParser

__all__ = ["WiktionaryDictionaryService"]


class WiktionaryDictionaryService:
    """Runtime service for querying locally cached Wiktionary dictionary data."""

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
            auto_build_missing: build Wiktionary data automatically if missing
            local_data_dir_path: optional local canonical data directory override
            runtime_data_dir_path: optional runtime canonical data directory override
        """
        if database_path is None:
            database_path = (
                get_runtime_cache_dir_path("dictionaries", "wiktionary")
                / "wiktionary.db"
            )
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.auto_build_missing = auto_build_missing
        self.database = DictionarySqliteStore(database_path=self.database_path)
        self.parser = WiktionaryDictionaryParser()

        self.local_data_dir_path = (
            local_data_dir_path
            if local_data_dir_path is not None
            else WIKTIONARY_LOCAL_JSONL_PATH.parent
        )
        self.runtime_data_dir_path = (
            runtime_data_dir_path
            if runtime_data_dir_path is not None
            else get_runtime_cache_dir_path("dictionaries", "wiktionary", "data")
        )

    def build(
        self,
        *,
        overwrite: bool = False,
        force_download: bool = False,
        source_jsonl_path: Path | None = None,
        update_local_data: bool = False,
    ) -> Path:
        """Build or rebuild the local Wiktionary SQLite dictionary.

        Arguments:
            overwrite: whether to overwrite an existing SQLite database
            force_download: force fresh Kaikki JSONL download before build
            source_jsonl_path: optional explicit path to Kaikki JSONL source dump
            update_local_data: update canonical local JSONL in repository data directory
        Returns:
            SQLite database path
        """
        if self.database_path.exists() and not overwrite:
            return self.database_path

        resolved_source_jsonl_path = self._require_source_jsonl_path(
            force_download=force_download,
            source_jsonl_path=source_jsonl_path,
            update_local_data=update_local_data,
        )
        parsed_data = self.parser.parse(source_jsonl_path=resolved_source_jsonl_path)
        return self.database.persist(parsed_data)

    def lookup(self, query: str, limit: int = 10) -> list[DictionaryEntry]:
        """Query local Wiktionary data using inferred query formats.

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

    def _copy_jsonl_to_local(self, *, source_jsonl_path: Path) -> Path:
        """Copy one canonical JSONL source into the repository-local snapshot.

        Arguments:
            source_jsonl_path: source JSONL path
        Returns:
            local canonical JSONL path
        """
        local_jsonl_path = self.local_data_dir_path / "entries.jsonl"
        self.local_data_dir_path.mkdir(parents=True, exist_ok=True)
        if not (
            local_jsonl_path.exists()
            and source_jsonl_path.exists()
            and local_jsonl_path.samefile(source_jsonl_path)
        ):
            shutil.copy2(source_jsonl_path, local_jsonl_path)
        return val_input_path(local_jsonl_path)

    def _copy_jsonl_to_runtime(self, *, source_jsonl_path: Path) -> Path:
        """Copy one canonical JSONL source into runtime cache.

        Arguments:
            source_jsonl_path: source JSONL path
        Returns:
            runtime canonical JSONL path
        """
        runtime_jsonl_path = self.runtime_data_dir_path / "entries.jsonl"
        self.runtime_data_dir_path.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_jsonl_path, runtime_jsonl_path)
        return val_input_path(runtime_jsonl_path)

    def _ensure_database(self):
        """Ensure the SQLite database exists, building it if configured."""
        if self.database_path.exists():
            return
        if not self.auto_build_missing:
            raise FileNotFoundError(
                "Wiktionary dictionary database not found. "
                "Set auto_build_missing=True to build automatically, "
                "or build explicitly with WiktionaryDictionaryService.build()."
            )
        self.build(overwrite=False)

    def _download_to_runtime_jsonl(self) -> Path:
        """Download Kaikki Chinese JSONL to the runtime canonical path.

        Returns:
            runtime canonical JSONL path
        """
        runtime_jsonl_path = self.runtime_data_dir_path / "entries.jsonl"
        self.runtime_data_dir_path.mkdir(parents=True, exist_ok=True)
        with requests.get(
            WIKTIONARY_KAIKKI_JSONL_URL, stream=True, timeout=60.0
        ) as resp:
            resp.raise_for_status()
            with runtime_jsonl_path.open("wb") as outfile:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        outfile.write(chunk)
        return val_input_path(runtime_jsonl_path)

    def _require_source_jsonl_path(
        self,
        *,
        force_download: bool,
        source_jsonl_path: Path | None,
        update_local_data: bool,
    ) -> Path:
        """Resolve canonical source JSONL path for one build run.

        Arguments:
            force_download: force fresh Kaikki JSONL download before build
            source_jsonl_path: optional explicit path to Kaikki JSONL source dump
            update_local_data: update canonical local JSONL in repository data directory
        Returns:
            canonical source JSONL path
        """
        local_jsonl_path = self.local_data_dir_path / "entries.jsonl"
        runtime_jsonl_path = self.runtime_data_dir_path / "entries.jsonl"
        resolved_source_jsonl_path: Path

        if source_jsonl_path is not None:
            validated_source_jsonl_path = val_input_path(source_jsonl_path)
            resolved_source_jsonl_path = self._copy_jsonl_to_runtime(
                source_jsonl_path=validated_source_jsonl_path
            )
        elif not force_download and local_jsonl_path.exists():
            resolved_source_jsonl_path = val_input_path(local_jsonl_path)
        elif not force_download and runtime_jsonl_path.exists():
            resolved_source_jsonl_path = val_input_path(runtime_jsonl_path)
        else:
            resolved_source_jsonl_path = self._download_to_runtime_jsonl()

        if update_local_data:
            resolved_source_jsonl_path = self._copy_jsonl_to_local(
                source_jsonl_path=resolved_source_jsonl_path
            )
        return resolved_source_jsonl_path
