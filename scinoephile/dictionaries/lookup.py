#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared lookup helpers for local dictionary services."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, cast

from .cuhk import CuhkDictionaryService
from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry
from .gzzj import GzzjDictionaryService
from .kaifangcidian import KaifangcidianDictionaryService

__all__ = [
    "AVAILABLE_DICTIONARY_NAMES",
    "DictionaryName",
    "lookup_dictionary_entries",
]

type DictionaryName = Literal["cuhk", "gzzj", "kaifangcidian"]

AVAILABLE_DICTIONARY_NAMES: tuple[DictionaryName, ...] = (
    "cuhk",
    "gzzj",
    "kaifangcidian",
)
"""Supported dictionary selectors."""

_DICTIONARY_SERVICES = {
    "cuhk": CuhkDictionaryService,
    "gzzj": GzzjDictionaryService,
    "kaifangcidian": KaifangcidianDictionaryService,
}
"""Dictionary service classes keyed by selector."""


def _dedupe_definitions(
    definitions: list[DictionaryDefinition],
) -> list[DictionaryDefinition]:
    """Deduplicate definitions while preserving order.

    Arguments:
        definitions: definition list
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


def _merge_entries(entries: list[DictionaryEntry]) -> list[DictionaryEntry]:
    """Merge duplicate entries while preserving definitions.

    Arguments:
        entries: raw aggregated dictionary entries
    Returns:
        merged dictionary entries
    """
    merged_entries: dict[tuple[str, str, str, str], DictionaryEntry] = {}
    for entry in entries:
        key = (
            entry.traditional,
            entry.simplified,
            entry.pinyin,
            entry.jyutping,
        )
        if key not in merged_entries:
            merged_entries[key] = entry
            continue
        existing_entry = merged_entries[key]
        merged_entries[key] = DictionaryEntry(
            traditional=existing_entry.traditional,
            simplified=existing_entry.simplified,
            pinyin=existing_entry.pinyin,
            jyutping=existing_entry.jyutping,
            frequency=max(existing_entry.frequency, entry.frequency),
            definitions=_dedupe_definitions(
                [*existing_entry.definitions, *entry.definitions]
            ),
        )
    return list(merged_entries.values())


def _normalize_dictionary_names(
    dictionaries: list[str] | tuple[str, ...] | None,
) -> list[DictionaryName]:
    """Normalize requested dictionary names.

    Arguments:
        dictionaries: requested dictionary names, or None for all
    Returns:
        normalized dictionary names
    Raises:
        ValueError: unsupported dictionary name was requested
    """
    if dictionaries is None:
        return list(AVAILABLE_DICTIONARY_NAMES)

    normalized_names: list[DictionaryName] = []
    for dictionary_name in dictionaries:
        normalized_name = dictionary_name.strip().lower()
        if not normalized_name:
            continue
        if normalized_name == "all":
            return list(AVAILABLE_DICTIONARY_NAMES)
        if normalized_name not in AVAILABLE_DICTIONARY_NAMES:
            raise ValueError(f"Unsupported dictionary {dictionary_name!r}")
        typed_name = cast(DictionaryName, normalized_name)
        if typed_name not in normalized_names:
            normalized_names.append(typed_name)

    if normalized_names:
        return normalized_names
    return list(AVAILABLE_DICTIONARY_NAMES)


def lookup_dictionary_entries(
    *,
    query: str,
    limit: int,
    dictionaries: list[str] | tuple[str, ...] | None = None,
    database_path: Path | None = None,
    auto_build_missing: bool = False,
) -> list[DictionaryEntry]:
    """Search one or more configured dictionaries.

    Arguments:
        query: lookup query
        limit: max results per dictionary
        dictionaries: dictionary selectors, or None for all available selectors
        database_path: optional explicit database path for a single dictionary
        auto_build_missing: build a missing dictionary if supported
    Returns:
        merged dictionary entries
    Raises:
        FileNotFoundError: no requested databases were available
        ValueError: dictionaries or database_path were invalid
    """
    dictionary_names = _normalize_dictionary_names(dictionaries)
    if database_path is not None and len(dictionary_names) != 1:
        raise ValueError(
            "database_path may only be used when searching a single dictionary"
        )

    entries: list[DictionaryEntry] = []
    missing_dictionaries: list[DictionaryName] = []
    aggregate_lookup = len(dictionary_names) > 1
    available_dictionary_count = 0
    for dictionary_name in dictionary_names:
        service = _DICTIONARY_SERVICES[dictionary_name](
            database_path=database_path,
            auto_build_missing=auto_build_missing,
        )
        try:
            entries.extend(service.lookup(query=query, limit=limit))
            available_dictionary_count += 1
        except FileNotFoundError:
            if not aggregate_lookup:
                raise
            missing_dictionaries.append(dictionary_name)

    if entries or available_dictionary_count > 0:
        return _merge_entries(entries)

    if missing_dictionaries:
        missing_display = ", ".join(sorted(missing_dictionaries))
        raise FileNotFoundError(
            "No searchable dictionary databases were found. Build one or more "
            f"of: {missing_display}."
        )
    return []
