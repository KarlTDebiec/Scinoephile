#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core optimization SQL helpers."""

from __future__ import annotations

from collections.abc import Mapping

_DatabaseValue = str | int | float | bytes | None
"""Scalar value loaded from a SQL database row."""

__all__ = [
    "get_prefixed_payload",
    "get_unprefixed_payload",
    "quote_identifier",
]


def get_prefixed_payload(prefix: str, payload: dict) -> dict[str, object]:
    """Get a flat payload using table-column prefixes.

    Arguments:
        prefix: column prefix
        payload: payload to flatten
    Returns:
        flattened payload
    """
    return {f"{prefix}__{key}": value for key, value in sorted(payload.items())}


def get_unprefixed_payload(row: Mapping[str, _DatabaseValue], prefix: str) -> dict:
    """Get a nested payload from row columns matching a prefix.

    Arguments:
        row: database row mapping
        prefix: column prefix
    Returns:
        nested payload
    """
    column_prefix = f"{prefix}__"
    return {
        key.removeprefix(column_prefix): row[key]
        for key in row.keys()
        if key.startswith(column_prefix) and row[key] is not None
    }


def quote_identifier(identifier: str) -> str:
    """Quote a SQLite identifier.

    Arguments:
        identifier: SQLite identifier
    Returns:
        quoted identifier
    """
    return '"' + identifier.replace('"', '""') + '"'
