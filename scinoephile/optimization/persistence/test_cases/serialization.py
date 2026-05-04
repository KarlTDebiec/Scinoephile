#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Serialization helpers for persisted LLM test case payloads."""

from __future__ import annotations

import json
import sqlite3

__all__ = [
    "get_prefixed_payload",
    "get_unprefixed_payload",
]


def get_prefixed_payload(prefix: str, payload: dict) -> dict[str, object]:
    """Get a flat payload using table-column prefixes.

    Arguments:
        prefix: column prefix
        payload: payload to flatten
    Returns:
        flattened payload
    """
    return {
        f"{prefix}__{key}": _serialize_value(value)
        for key, value in sorted(payload.items())
    }


def get_unprefixed_payload(row: sqlite3.Row, prefix: str) -> dict:
    """Get a nested payload from row columns matching a prefix.

    Arguments:
        row: SQLite row
        prefix: column prefix
    Returns:
        nested payload
    """
    column_prefix = f"{prefix}__"
    return {
        key.removeprefix(column_prefix): _deserialize_value(row[key])
        for key in row.keys()
        if key.startswith(column_prefix) and row[key] is not None
    }


def _deserialize_value(value: object) -> object:
    """Deserialize a value loaded from SQLite.

    Arguments:
        value: value loaded from SQLite
    Returns:
        deserialized value
    """
    if isinstance(value, str) and value.startswith(("[", "{")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _serialize_value(value: object) -> object:
    """Serialize a value for storage in SQLite.

    Arguments:
        value: value to serialize
    Returns:
        serialized value
    """
    if isinstance(value, dict | list):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return value
