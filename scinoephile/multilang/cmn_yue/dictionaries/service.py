#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Aggregate lookup service for 中文/粤文 dictionaries."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.validation import val_int
from scinoephile.core.dictionaries import (
    DictionaryLookupResult,
    DictionarySource,
    DictionarySqliteStore,
    LookupDirection,
)
from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings
from scinoephile.lang.yue.romanization import get_yue_jyutping_query_strings

from .constants import MAX_LOOKUP_LIMIT
from .registry import (
    get_cmn_yue_dictionary_source_spec,
    get_installed_cmn_yue_dictionary_source_specs,
    infer_cmn_yue_dictionary_source_id,
    normalize_cmn_yue_dictionary_source_name,
    resolve_registered_cmn_yue_dictionary_source_ids,
)

__all__ = [
    "CmnYueDictionaryService",
]


class CmnYueDictionaryService:
    """Aggregate lookup service across installed 中文/粤文 dictionary databases."""

    def __init__(self, database_paths: list[Path] | None = None):
        """Initialize.

        Arguments:
            database_paths: explicit SQLite database paths to search; if omitted,
              registered installed-source paths are used
        """
        self.database_paths = None if database_paths is None else list(database_paths)

    def lookup(
        self,
        query: str,
        direction: LookupDirection = LookupDirection.CMN_TO_YUE,
        limit: int = 10,
        source_ids: list[str] | None = None,
    ) -> list[DictionaryLookupResult]:
        """Query one or more installed dictionary databases.

        Arguments:
            query: input text to search
            direction: lookup direction
            limit: max results to return
            source_ids: optional source filters
        Returns:
            source-tagged dictionary lookup results
        Raises:
            FileNotFoundError: if no matching databases are available
            ValueError: if requested source names are invalid
        """
        normalized_query = query.strip()
        if not normalized_query:
            return []
        limit = val_int(limit, min_value=1, max_value=MAX_LOOKUP_LIMIT)

        lookup_queries = self.get_lookup_queries(normalized_query, direction)
        database_specs = self._get_database_specs(source_ids)

        results: list[DictionaryLookupResult] = []
        for source_id, source, database_path in database_specs:
            remaining_limit = limit - len(results)
            if remaining_limit <= 0:
                break

            store = DictionarySqliteStore(database_path=database_path)
            for lookup_query in lookup_queries:
                entries = store.lookup(
                    lookup_query,
                    direction=direction,
                    limit=remaining_limit,
                )
                if not entries:
                    continue
                results.extend(
                    DictionaryLookupResult(
                        source_id=source_id,
                        source=source,
                        entry=entry,
                    )
                    for entry in entries
                )
                break

        return results

    @staticmethod
    def get_lookup_queries(query: str, direction: LookupDirection) -> list[str]:
        """Get ordered query variants for dictionary lookup.

        Arguments:
            query: raw query text
            direction: lookup direction
        Returns:
            ordered query variants
        """
        if direction == LookupDirection.CMN_TO_YUE:
            query_variants = get_cmn_pinyin_query_strings(query)
        else:
            query_variants = get_yue_jyutping_query_strings(query)

        ordered_queries: list[str] = []
        seen_queries: set[str] = set()
        for one_query in [*query_variants, query]:
            if one_query and one_query not in seen_queries:
                seen_queries.add(one_query)
                ordered_queries.append(one_query)
        return ordered_queries

    def _get_database_specs(
        self,
        source_ids: list[str] | None,
    ) -> list[tuple[str, DictionarySource, Path]]:
        """Resolve the database paths and source metadata to search.

        Arguments:
            source_ids: optional source filters
        Returns:
            tuples of source id, source metadata, and database path
        Raises:
            FileNotFoundError: if no matching databases are available
        """
        if self.database_paths is not None:
            return self._get_explicit_database_specs(source_ids)
        return self._get_registered_database_specs(source_ids)

    def _get_explicit_database_specs(
        self,
        source_ids: list[str] | None,
    ) -> list[tuple[str, DictionarySource, Path]]:
        """Resolve explicit database paths supplied by the caller.

        Arguments:
            source_ids: optional source filters
        Returns:
            tuples of source id, source metadata, and database path
        Raises:
            FileNotFoundError: if no matching databases are available
        """
        requested_source_ids = (
            None
            if source_ids is None
            else {
                normalize_cmn_yue_dictionary_source_name(source_id)
                for source_id in source_ids
            }
        )
        matched_source_ids: set[str] = set()
        database_specs: list[tuple[str, DictionarySource, Path]] = []

        for database_path in self.database_paths or []:
            store = DictionarySqliteStore(database_path=database_path)
            source = store.load_source()
            source_id = infer_cmn_yue_dictionary_source_id(source)
            candidate_source_ids = {
                normalize_cmn_yue_dictionary_source_name(source_id),
                normalize_cmn_yue_dictionary_source_name(source.shortname),
                normalize_cmn_yue_dictionary_source_name(source.name),
            }
            if requested_source_ids is not None and candidate_source_ids.isdisjoint(
                requested_source_ids
            ):
                continue
            if requested_source_ids is not None:
                matched_source_ids.update(candidate_source_ids & requested_source_ids)
            database_specs.append((source_id, source, database_path))

        if requested_source_ids is not None:
            missing_source_ids = sorted(requested_source_ids - matched_source_ids)
            if missing_source_ids:
                raise FileNotFoundError(
                    "Requested dictionary source(s) not found in the provided "
                    f"database path(s): {', '.join(missing_source_ids)}"
                )
        if not database_specs:
            raise FileNotFoundError(
                "No dictionary databases matched the provided path(s)"
            )
        return database_specs

    @staticmethod
    def _get_registered_database_specs(
        source_ids: list[str] | None,
    ) -> list[tuple[str, DictionarySource, Path]]:
        """Resolve registered installed database paths.

        Arguments:
            source_ids: optional source filters
        Returns:
            tuples of source id, source metadata, and database path
        Raises:
            FileNotFoundError: if requested or installed databases are missing
        """
        database_specs: list[tuple[str, DictionarySource, Path]] = []

        if source_ids is None:
            source_specs = get_installed_cmn_yue_dictionary_source_specs()
            if not source_specs:
                raise FileNotFoundError("No installed dictionary databases were found")
            for source_spec in source_specs:
                database_path = source_spec.get_default_database_path()
                store = DictionarySqliteStore(database_path=database_path)
                database_specs.append(
                    (source_spec.source_id, store.load_source(), database_path)
                )
            return database_specs

        resolved_source_ids = resolve_registered_cmn_yue_dictionary_source_ids(
            source_ids
        )
        missing_source_ids: list[str] = []
        for resolved_source_id in resolved_source_ids:
            source_spec = get_cmn_yue_dictionary_source_spec(resolved_source_id)
            database_path = source_spec.get_default_database_path()
            if not database_path.exists():
                missing_source_ids.append(resolved_source_id)
                continue
            store = DictionarySqliteStore(database_path=database_path)
            database_specs.append(
                (resolved_source_id, store.load_source(), database_path)
            )

        if missing_source_ids:
            raise FileNotFoundError(
                "Requested dictionary database(s) not found: "
                f"{', '.join(missing_source_ids)}"
            )
        return database_specs
