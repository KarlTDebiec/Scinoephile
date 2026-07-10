#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared SQLite infrastructure for optimization persistence."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from pydantic import JsonValue
from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.engine import URL, Connection
from sqlalchemy.event import listen
from sqlalchemy.pool import NullPool

from scinoephile.common.validation import val_output_path
from scinoephile.core.exceptions import ScinoephileError

__all__ = [
    "OptimizationSqliteStore",
    "load_json_object",
    "metadata",
    "serialize_json_object",
]

metadata = MetaData()
"""SQLAlchemy Core metadata for the optimization catalog."""


def load_json_object(value: object, subject: str) -> dict[str, JsonValue]:
    """Load a JSON object stored in a SQLite text column.

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
        loaded = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ScinoephileError(f"{subject} is invalid JSON.") from exc
    if not isinstance(loaded, dict):
        raise ScinoephileError(f"{subject} is not a JSON object.")
    return cast("dict[str, JsonValue]", loaded)


def serialize_json_object(value: Mapping[str, JsonValue]) -> str:
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
    """Shared SQLite connection and schema management for optimization data."""

    schema_version = 6
    """SQLite schema version."""

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
        """Create the current SQLite schema if needed.

        Raises:
            ScinoephileError: if the database uses an unsupported schema version
        """
        self.database_path = val_output_path(self.database_path, exist_ok=True)
        with self.engine.begin() as connection:
            version = self._get_schema_version(connection)
            if version not in {0, self.schema_version}:
                raise ScinoephileError(
                    f"SQLite optimization schema version {version} is unsupported; "
                    "create a new database."
                )
            metadata.create_all(connection)
            connection.execute(text(f"PRAGMA user_version={self.schema_version}"))

    @staticmethod
    def _enable_sqlite_foreign_keys(
        dbapi_connection: Any,
        _connection_record: object,
    ):
        """Enable SQLite foreign-key enforcement on a new DB-API connection."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    @staticmethod
    def _get_schema_version(connection: Connection) -> int:
        """Get the SQLite user schema version.

        Arguments:
            connection: SQLAlchemy connection
        Returns:
            SQLite user schema version
        """
        return int(connection.execute(text("PRAGMA user_version")).scalar_one())

    @classmethod
    def _require_current_schema(cls, version: int):
        """Require the current optimization schema version.

        Arguments:
            version: SQLite user schema version
        Raises:
            ScinoephileError: if the schema version is unsupported
        """
        if version != cls.schema_version:
            raise ScinoephileError(
                f"SQLite optimization schema version {version} is unsupported; "
                "create a new database."
            )
