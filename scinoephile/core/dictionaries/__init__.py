#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core dictionary models and shared lookup metadata.

Package hierarchy (modules may import from any above):
* dictionary_definition / dictionary_lookup_response / dictionary_source
  / dictionary_tool_prompt
* dictionary_entry
* serialization / sqlite_store
"""

from __future__ import annotations

from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry
from .dictionary_lookup_response import DictionaryLookupResponse
from .dictionary_source import DictionarySource
from .dictionary_tool_prompt import DictionaryToolPrompt
from .sqlite_store import DictionarySqliteStore

__all__ = [
    "DictionaryDefinition",
    "DictionaryEntry",
    "DictionaryLookupResponse",
    "DictionarySource",
    "DictionarySqliteStore",
    "DictionaryToolPrompt",
]
