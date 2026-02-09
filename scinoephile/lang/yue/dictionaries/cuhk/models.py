#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Data models shared by Cantonese dictionary pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "DictionaryDefinition",
    "DictionaryEntry",
    "DictionarySource",
]


@dataclass(frozen=True)
class DictionarySource:
    """Metadata describing a dictionary source."""

    name: str
    shortname: str
    version: str
    description: str
    legal: str
    link: str
    update_url: str
    other: str


@dataclass(frozen=True)
class DictionaryDefinition:
    """Definition metadata tied to a dictionary entry."""

    text: str
    label: str = ""


@dataclass(frozen=True)
class DictionaryEntry:
    """Normalized dictionary entry."""

    traditional: str
    simplified: str
    pinyin: str
    jyutping: str
    frequency: float = 0.0
    definitions: list[DictionaryDefinition] = field(default_factory=list)
