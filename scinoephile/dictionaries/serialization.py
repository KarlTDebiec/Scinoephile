#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Serialization helpers for dictionary models."""

from __future__ import annotations

from .dictionary_definition import DictionaryDefinition
from .dictionary_entry import DictionaryEntry

__all__ = [
    "dictionary_definition_to_dict",
    "dictionary_entry_to_dict",
]


def dictionary_definition_to_dict(definition: DictionaryDefinition) -> dict[str, str]:
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


def dictionary_entry_to_dict(
    entry: DictionaryEntry,
) -> dict[str, str | float | list[dict[str, str]]]:
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
