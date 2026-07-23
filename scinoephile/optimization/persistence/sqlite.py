#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared SQLite infrastructure for optimization persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import ClassVar

from pydantic import JsonValue
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import URL
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.event import listen
from sqlalchemy.pool import ConnectionPoolEntry, NullPool

from scinoephile.common.validation import val_output_path
from scinoephile.core.exceptions import ScinoephileError

__all__ = [
    "OptimizationSqliteStore",
    "deserialize_json",
    "serialize_json",
]


def deserialize_json(value: object, subject: str) -> dict[str, JsonValue]:
    """Deserialize a JSON object stored in a SQLite text column.

    Arguments:
        value: SQLite column value
        subject: subject used in corruption errors
    Returns:
        loaded JSON object
    Raises:
        ScinoephileError: if the stored value is not a JSON object
    """
    if not isinstance(value, str):
        raise ScinoephileError(f"{subject} is not JSON text.")
    try:
        loaded: JsonValue = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ScinoephileError(f"{subject} is invalid JSON.") from exc
    if not isinstance(loaded, dict):
        raise ScinoephileError(f"{subject} is not a JSON object.")
    return loaded


def serialize_json(value: dict[str, JsonValue]) -> str:
    """Serialize a JSON object canonically for SQLite storage.

    Arguments:
        value: JSON object
    Returns:
        canonical JSON text
    """
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


class OptimizationSqliteStore:
    """Shared SQLite connection infrastructure for optimization data."""

    _metadata: ClassVar[MetaData]
    """Component-owned SQLAlchemy metadata."""

    def __init__(self, database_path: Path):
        """Initialize.

        Arguments:
            database_path: SQLite database path
        """
        self.database_path = val_output_path(
            database_path,
            exist_ok=True,
            create=False,
        )
        self.engine = create_engine(
            URL.create("sqlite", database=str(self.database_path)),
            future=True,
            poolclass=NullPool,
        )
        listen(self.engine, "connect", self._enable_sqlite_foreign_keys)

    def create_schema(self):
        """Create this store's tables if needed."""
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self.engine.begin() as connection:
            self._metadata.create_all(connection)

    @staticmethod
    def _enable_sqlite_foreign_keys(
        dbapi_connection: DBAPIConnection,
        _connection_record: ConnectionPoolEntry,
    ):
        """Enable SQLite foreign-key enforcement on a new DB-API connection.

        Arguments:
            dbapi_connection: newly opened DB-API connection
            _connection_record: SQLAlchemy pool record for the connection
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
