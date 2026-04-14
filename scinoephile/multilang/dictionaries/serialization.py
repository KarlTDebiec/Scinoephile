#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Serialization helpers for dictionary models."""

from __future__ import annotations

from typing import TypedDict

from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry

__all__ = [
    "DictionaryDefinitionDict",
    "DictionaryEntryDict",
    "dictionary_definition_to_dict",
    "dictionary_entry_to_dict",
]


class DictionaryDefinitionDict(TypedDict):
    """JSON-serializable dictionary definition payload."""

    label: str
    """Optional part-of-speech or usage label for the definition."""

    text: str
    """Definition text associated with the dictionary entry."""


class DictionaryEntryDict(TypedDict):
    """JSON-serializable dictionary entry payload."""

    traditional: str
    """Traditional Chinese headword text."""

    simplified: str
    """Simplified Chinese headword text."""

    pinyin: str
    """Mandarin pronunciation written in pinyin."""

    jyutping: str
    """Cantonese pronunciation written in Jyutping."""

    frequency: float
    """Frequency score used to rank or compare entries."""

    definitions: list[DictionaryDefinitionDict]
    """Definitions associated with this entry."""


def dictionary_definition_to_dict(
    definition: DictionaryDefinition,
) -> DictionaryDefinitionDict:
    """Convert one dictionary definition into a JSON-serializable payload.

    Arguments:
        definition: dictionary definition
    Returns:
        serialized dictionary definition
    """
    return {
        "label": definition.label,
        "text": definition.text,
    }


def dictionary_entry_to_dict(entry: DictionaryEntry) -> DictionaryEntryDict:
    """Convert one dictionary entry into a JSON-serializable payload.

    Arguments:
        entry: dictionary entry
    Returns:
        serialized dictionary entry
    """
    return {
        "traditional": entry.traditional,
        "simplified": entry.simplified,
        "pinyin": entry.pinyin,
        "jyutping": entry.jyutping,
        "frequency": entry.frequency,
        "definitions": [
            dictionary_definition_to_dict(definition)
            for definition in entry.definitions
        ],
    }
