#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Model class for dictionary entries."""

from __future__ import annotations

from dataclasses import dataclass, field

from .dictionary_definition import DictionaryDefinition

__all__ = ["DictionaryEntry"]


@dataclass(frozen=True)
class DictionaryEntry:
    """Normalized dictionary entry."""

    traditional: str
    """Traditional Chinese headword text."""

    simplified: str
    """Simplified Chinese headword text."""

    pinyin: str
    """Mandarin pronunciation written in pinyin."""

    jyutping: str
    """Cantonese pronunciation written in Jyutping."""

    frequency: float = 0.0
    """Frequency score used to rank or compare entries."""

    definitions: list[DictionaryDefinition] = field(default_factory=list)
    """Definitions associated with this entry."""
