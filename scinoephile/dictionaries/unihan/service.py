#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Unihan dictionary service."""

from __future__ import annotations

import shutil
import zipfile
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
    UNIHAN_LOCAL_DATA_DIR_PATH,
    UNIHAN_REQUIRED_SOURCE_FILENAMES,
    UNIHAN_ZIP_URL,
)
from .parser import UnihanDictionaryParser

__all__ = ["UnihanDictionaryService"]


class UnihanDictionaryService:
    """Runtime service for querying locally cached Unihan dictionary data."""

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
            auto_build_missing: build Unihan data automatically if missing
            local_data_dir_path: optional local canonical data directory override
            runtime_data_dir_path: optional runtime canonical data directory override
        """
        if database_path is None:
            database_path = (
                get_runtime_cache_dir_path("dictionaries", "unihan") / "unihan.db"
            )
        self.database_path = val_output_path(database_path, exist_ok=True)
        self.auto_build_missing = auto_build_missing
        self.database = DictionarySqliteStore(database_path=self.database_path)
        self.parser = UnihanDictionaryParser()

        self.local_data_dir_path = (
            local_data_dir_path
            if local_data_dir_path is not None
            else UNIHAN_LOCAL_DATA_DIR_PATH
        )
        self.runtime_data_dir_path = (
            runtime_data_dir_path
            if runtime_data_dir_path is not None
            else get_runtime_cache_dir_path("dictionaries", "unihan", "data")
        )

    def build(
        self,
        *,
        overwrite: bool = False,
        force_download: bool = False,
        update_local_data: bool = False,
        source_dictionary_like_data_path: Path | None = None,
        source_readings_path: Path | None = None,
        source_variants_path: Path | None = None,
    ) -> Path:
        """Build or rebuild the local Unihan SQLite dictionary.

        Arguments:
            overwrite: whether to overwrite an existing SQLite database
            force_download: force fresh Unihan.zip download before build
            update_local_data: update canonical local files in repository data directory
            source_dictionary_like_data_path: optional explicit DictionaryLikeData path
            source_readings_path: optional explicit Readings path
            source_variants_path: optional explicit Variants path
        Returns:
            SQLite database path
        """
        if self.database_path.exists() and not overwrite:
            return self.database_path

        source_paths = self._require_source_paths(
            force_download=force_download,
            update_local_data=update_local_data,
            source_dictionary_like_data_path=source_dictionary_like_data_path,
            source_readings_path=source_readings_path,
            source_variants_path=source_variants_path,
        )
        parsed_data = self.parser.parse(
            dictionary_like_data_path=source_paths["Unihan_DictionaryLikeData.txt"],
            readings_path=source_paths["Unihan_Readings.txt"],
            variants_path=source_paths["Unihan_Variants.txt"],
        )
        return self.database.persist(parsed_data)

    def lookup(self, query: str, limit: int = 10) -> list[DictionaryEntry]:
        """Query local Unihan dictionary data using inferred query formats.

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
                "Unihan dictionary database not found. "
                "Set auto_build_missing=True to build automatically, "
                "or build explicitly with UnihanDictionaryService.build()."
            )
        self.build(overwrite=False)

    def _copy_sources_to_local(self, source_paths: dict[str, Path]) -> dict[str, Path]:
        """Copy source files into repository-local data snapshots.

        Arguments:
            source_paths: source path mapping
        Returns:
            validated local path mapping
        """
        self.local_data_dir_path.mkdir(parents=True, exist_ok=True)
        local_paths = self._get_required_paths(self.local_data_dir_path)
        for filename, source_path in source_paths.items():
            shutil.copy2(source_path, local_paths[filename])
        return self._validate_paths(local_paths)

    def _download_and_extract_to_runtime(self) -> dict[str, Path]:
        """Download Unihan.zip and extract required files to runtime cache.

        Returns:
            validated extracted file paths keyed by filename
        """
        self.runtime_data_dir_path.mkdir(parents=True, exist_ok=True)
        zip_path = self.runtime_data_dir_path / "Unihan.zip"
        response = requests.get(UNIHAN_ZIP_URL, timeout=60.0)
        response.raise_for_status()
        zip_path.write_bytes(response.content)

        extracted_paths = self._get_required_paths(self.runtime_data_dir_path)
        with zipfile.ZipFile(zip_path, mode="r") as archive:
            for filename in UNIHAN_REQUIRED_SOURCE_FILENAMES:
                target_path = extracted_paths[filename]
                try:
                    with archive.open(filename, mode="r") as src:
                        target_path.write_bytes(src.read())
                except KeyError as exc:
                    raise FileNotFoundError(
                        f"Required file {filename!r} not found in downloaded Unihan.zip"
                    ) from exc
        return self._validate_paths(extracted_paths)

    def _require_source_paths(
        self,
        *,
        force_download: bool,
        update_local_data: bool,
        source_dictionary_like_data_path: Path | None,
        source_readings_path: Path | None,
        source_variants_path: Path | None,
    ) -> dict[str, Path]:
        """Get required source files, downloading and extracting if needed.

        Arguments:
            force_download: force fresh Unihan.zip download before build
            update_local_data: update canonical local files in repository data directory
            source_dictionary_like_data_path: optional explicit DictionaryLikeData path
            source_readings_path: optional explicit Readings path
            source_variants_path: optional explicit Variants path
        Returns:
            resolved source file paths keyed by required filename
        """
        explicit_paths = {
            "Unihan_DictionaryLikeData.txt": source_dictionary_like_data_path,
            "Unihan_Readings.txt": source_readings_path,
            "Unihan_Variants.txt": source_variants_path,
        }
        if any(path is not None for path in explicit_paths.values()):
            return self._resolve_explicit_source_paths(explicit_paths)

        local_paths = self._get_required_paths(self.local_data_dir_path)
        if not force_download and self._all_paths_exist(local_paths):
            return self._validate_paths(local_paths)

        runtime_paths = self._get_required_paths(self.runtime_data_dir_path)
        if not force_download and self._all_paths_exist(runtime_paths):
            validated_runtime_paths = self._validate_paths(runtime_paths)
            if update_local_data:
                return self._copy_sources_to_local(validated_runtime_paths)
            return validated_runtime_paths

        downloaded_paths = self._download_and_extract_to_runtime()
        if update_local_data:
            return self._copy_sources_to_local(downloaded_paths)
        return downloaded_paths

    def _resolve_explicit_source_paths(
        self,
        explicit_paths: dict[str, Path | None],
    ) -> dict[str, Path]:
        """Resolve optional explicit source path overrides.

        Arguments:
            explicit_paths: explicit source path mapping
        Returns:
            validated source paths keyed by filename
        """
        resolved_paths: dict[str, Path] = {}
        defaults = self._get_required_paths(self.local_data_dir_path)
        for filename, explicit_path in explicit_paths.items():
            source_path = defaults[filename] if explicit_path is None else explicit_path
            resolved_paths[filename] = val_input_path(source_path)
        return resolved_paths

    @staticmethod
    def _all_paths_exist(paths: dict[str, Path]) -> bool:
        """Check whether all required paths exist.

        Arguments:
            paths: path mapping
        Returns:
            whether all paths exist
        """
        return all(path.exists() for path in paths.values())

    @staticmethod
    def _get_required_paths(base_dir_path: Path) -> dict[str, Path]:
        """Get required Unihan source paths under one directory.

        Arguments:
            base_dir_path: source directory path
        Returns:
            required source paths keyed by filename
        """
        return {
            filename: base_dir_path / filename
            for filename in UNIHAN_REQUIRED_SOURCE_FILENAMES
        }

    @staticmethod
    def _validate_paths(paths: dict[str, Path]) -> dict[str, Path]:
        """Validate required source paths.

        Arguments:
            paths: source path mapping
        Returns:
            validated source path mapping
        """
        return {name: val_input_path(path) for name, path in paths.items()}
