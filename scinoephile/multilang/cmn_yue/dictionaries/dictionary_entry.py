#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Model class for normalized dictionary entries."""

from __future__ import annotations

from dataclasses import dataclass, field

from .dictionary_definition import DictionaryDefinition

__all__ = [
    "DictionaryEntry",
]


@dataclass(frozen=True)
class DictionaryEntry:
    """Normalized dictionary entry."""

    traditional: str
    simplified: str
    pinyin: str
    jyutping: str
    frequency: float = 0.0
    definitions: list[DictionaryDefinition] = field(default_factory=list)
