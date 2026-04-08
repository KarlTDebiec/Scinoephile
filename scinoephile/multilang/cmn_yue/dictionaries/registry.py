#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Registry and source-id helpers for 中文/粤文 dictionaries."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from scinoephile.core.dictionaries import DictionarySource
from scinoephile.core.paths import get_runtime_cache_dir_path

from .cuhk.constants import CUHK_SOURCE

__all__ = [
    "CmnYueDictionarySourceSpec",
    "get_cmn_yue_dictionary_source_spec",
    "get_cmn_yue_dictionary_source_specs",
    "get_installed_cmn_yue_dictionary_source_specs",
    "infer_cmn_yue_dictionary_source_id",
    "normalize_cmn_yue_dictionary_source_name",
    "resolve_registered_cmn_yue_dictionary_source_ids",
]


NON_WORD_REGEX = re.compile(r"\W+")


@dataclass(frozen=True)
class CmnYueDictionarySourceSpec:
    """Registry metadata for one installed dictionary source."""

    source_id: str
    """Normalized identifier used in CLI and tool filtering."""

    source: DictionarySource
    """Dictionary source metadata expected for the installed database."""

    aliases: tuple[str, ...] = ()
    """Additional human-entered labels accepted for this source."""

    def get_default_database_path(self) -> Path:
        """Get the default database path for this source.

        Returns:
            default SQLite database path
        """
        return (
            get_runtime_cache_dir_path("dictionaries", self.source_id)
            / f"{self.source_id}.db"
        )

    def matches(self, source_name: str) -> bool:
        """Check whether a user-provided label refers to this source.

        Arguments:
            source_name: user-provided source label
        Returns:
            whether the label matches this source
        """
        normalized_source_name = normalize_cmn_yue_dictionary_source_name(source_name)
        candidate_names = (
            self.source_id,
            self.source.shortname,
            self.source.name,
            *self.aliases,
        )
        return normalized_source_name in {
            normalize_cmn_yue_dictionary_source_name(candidate_name)
            for candidate_name in candidate_names
        }


def get_cmn_yue_dictionary_source_specs() -> tuple[CmnYueDictionarySourceSpec, ...]:
    """Get registered 中文/粤文 dictionary source specifications.

    Returns:
        registered source specifications in search priority order
    """
    return (
        CmnYueDictionarySourceSpec(
            source_id="cuhk",
            source=CUHK_SOURCE,
        ),
    )


def get_cmn_yue_dictionary_source_spec(source_name: str) -> CmnYueDictionarySourceSpec:
    """Get one registered source specification by label.

    Arguments:
        source_name: user-provided source label
    Returns:
        matching source specification
    Raises:
        ValueError: if the label does not match a registered source
    """
    for source_spec in get_cmn_yue_dictionary_source_specs():
        if source_spec.matches(source_name):
            return source_spec
    raise ValueError(f"Unknown dictionary source: {source_name}")


def get_installed_cmn_yue_dictionary_source_specs() -> list[CmnYueDictionarySourceSpec]:
    """Get registered sources whose default databases are installed locally.

    Returns:
        installed registered source specifications
    """
    return [
        source_spec
        for source_spec in get_cmn_yue_dictionary_source_specs()
        if source_spec.get_default_database_path().exists()
    ]


def infer_cmn_yue_dictionary_source_id(source: DictionarySource) -> str:
    """Infer a normalized source identifier from source metadata.

    Arguments:
        source: source metadata loaded from SQLite
    Returns:
        normalized source identifier
    """
    for candidate_name in (source.shortname, source.name):
        for source_spec in get_cmn_yue_dictionary_source_specs():
            if source_spec.matches(candidate_name):
                return source_spec.source_id
    return normalize_cmn_yue_dictionary_source_name(source.shortname or source.name)


def normalize_cmn_yue_dictionary_source_name(source_name: str) -> str:
    """Normalize a source label for matching and filtering.

    Arguments:
        source_name: raw source label
    Returns:
        normalized source label
    Raises:
        ValueError: if the normalized value would be empty
    """
    normalized_source_name = NON_WORD_REGEX.sub("_", source_name.strip().lower())
    normalized_source_name = normalized_source_name.strip("_")
    if not normalized_source_name:
        raise ValueError("Dictionary source names must be non-empty")
    return normalized_source_name


def resolve_registered_cmn_yue_dictionary_source_ids(
    source_names: list[str],
) -> list[str]:
    """Resolve one or more user labels to registered source identifiers.

    Arguments:
        source_names: user-provided source labels
    Returns:
        canonical registered source identifiers
    """
    resolved_source_ids: list[str] = []
    seen_source_ids: set[str] = set()
    for source_name in source_names:
        source_spec = get_cmn_yue_dictionary_source_spec(source_name)
        if source_spec.source_id not in seen_source_ids:
            seen_source_ids.add(source_spec.source_id)
            resolved_source_ids.append(source_spec.source_id)
    return resolved_source_ids
