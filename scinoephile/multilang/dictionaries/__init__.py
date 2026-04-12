#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared dictionary utilities across multilingual workflows."""

from __future__ import annotations

from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry
from .dictionary_source import DictionarySource
from .lookup_direction import LookupDirection
from .sqlite_store import DictionarySqliteStore

__all__ = [
    "DictionaryDefinition",
    "DictionaryEntry",
    "DictionarySource",
    "DictionarySqliteStore",
    "LookupDirection",
]
