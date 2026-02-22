#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CUHK dictionary package."""

from __future__ import annotations

from .builder import CuhkDictionaryBuilder
from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry
from .dictionary_source import DictionarySource
from .lookup_direction import LookupDirection
from .service import CuhkDictionaryService

__all__ = [
    "CuhkDictionaryBuilder",
    "CuhkDictionaryService",
    "DictionaryDefinition",
    "DictionaryEntry",
    "DictionarySource",
    "LookupDirection",
]
