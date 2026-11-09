#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""SQLite storage for audit progress and the published proofreading baseline."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from .models import AuditRow, AuditStatus

__all__ = [
    "backup_progress",
    "initialize_progress",
    "load_proofreading_settings",
    "load_saved_rows",
    "load_saved_source",
    "save_proofreading_progress",
    "save_rows",
]


def backup_progress(db: sqlite3.Connection, backup_path: Path):
    """Copy the review database before opening a write transaction.

    Arguments:
        db: live review database connection
        backup_path: destination database file
    """
    with closing(sqlite3.connect(backup_path)) as backup_db:
        db.backup(backup_db)


def initialize_progress(db: sqlite3.Connection, source_content: bytes):
    """Create the progress tables and record the published source.

    Arguments:
        db: review database connection
        source_content: published source SRT bytes
    """
    db.execute(
        "CREATE TABLE IF NOT EXISTS review_edits ("
        "key TEXT PRIMARY KEY, reviewed TEXT NOT NULL, "
        "review_note TEXT NOT NULL, notes TEXT NOT NULL, "
        "finding TEXT NOT NULL, verified INTEGER NOT NULL, "
        "version INTEGER NOT NULL)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS review_metadata ("
        "name TEXT PRIMARY KEY, value BLOB NOT NULL)"
    )
    _save_metadata(db, "source", source_content)


def load_proofreading_settings(db: sqlite3.Connection) -> dict[str, str]:
    """Load settings from the last successfully published proofreading run.

    Arguments:
        db: review database connection
    Returns:
        stored settings or an empty mapping
    """
    content = _load_metadata(db, "proofreading")
    if content is None:
        return {}
    return json.loads(content.decode("utf-8"))


def load_saved_rows(
    db: sqlite3.Connection, rows: list[AuditRow], *, match_review_note: bool
) -> list[AuditRow]:
    """Apply stored progress to the current subtitle rows.

    Arguments:
        db: review database connection
        rows: current rows built from the project's files
        match_review_note: whether the saved note must match the native decision
    Returns:
        current rows with saved versions and matching progress
    """
    saved = {
        row[0]: row[1:]
        for row in db.execute(
            "SELECT key, reviewed, review_note, notes, finding, verified, version "
            "FROM review_edits"
        )
    }
    loaded = []
    for row in rows:
        current = row
        if row.key in saved:
            text, note, notes, finding, verified, version = saved[row.key]
            current = replace(row, version=version)
            if text == row.reviewed and (
                not match_review_note or note == row.review_note
            ):
                current = replace(
                    current,
                    review_note=note,
                    notes=notes,
                    finding=AuditStatus(finding),
                    verified=bool(verified),
                )
        loaded.append(current)
    return loaded


def load_saved_source(db: sqlite3.Connection) -> bytes | None:
    """Read the published source from a previously opened review database.

    Arguments:
        db: existing review database connection
    Returns:
        source SRT bytes if the database has a stored baseline
    """
    if db.execute(
        "SELECT 1 FROM sqlite_master WHERE name='review_metadata'"
    ).fetchone():
        return _load_metadata(db, "source")
    return None


def save_proofreading_progress(
    db: sqlite3.Connection,
    previous_rows: list[AuditRow],
    rows: list[AuditRow],
    source_content: bytes,
    settings: dict[str, str] | None,
):
    """Replace progress for the prior source with the newly published baseline.

    Arguments:
        db: review database connection within the publication transaction
        previous_rows: prior baseline rows whose keys must be removed
        rows: updated baseline rows with current progress
        source_content: source SRT bytes for the new baseline
        settings: optional settings for the published proofreading run
    """
    db.executemany(
        "DELETE FROM review_edits WHERE key=?", [(row.key,) for row in previous_rows]
    )
    save_rows(db, rows)
    _save_metadata(db, "source", source_content)
    if settings is not None:
        _save_metadata(db, "proofreading", json.dumps(settings).encode("utf-8"))


def save_rows(db: sqlite3.Connection, rows: Iterable[AuditRow]):
    """Insert or update audit rows inside the caller's transaction.

    Arguments:
        db: review database connection
        rows: edited rows with their final version numbers
    """
    db.executemany(
        "INSERT INTO review_edits VALUES (?, ?, ?, ?, ?, ?, ?) "
        "ON CONFLICT(key) DO UPDATE SET reviewed=excluded.reviewed, "
        "review_note=excluded.review_note, notes=excluded.notes, "
        "finding=excluded.finding, verified=excluded.verified, "
        "version=excluded.version",
        (
            (
                row.key,
                row.reviewed,
                row.review_note,
                row.notes,
                row.finding,
                int(row.verified),
                row.version,
            )
            for row in rows
        ),
    )


def _load_metadata(db: sqlite3.Connection, name: str) -> bytes | None:
    """Read a stored metadata value.

    Arguments:
        db: review database connection
        name: metadata key
    Returns:
        stored bytes if the key exists
    """
    stored = db.execute(
        "SELECT value FROM review_metadata WHERE name=?", (name,)
    ).fetchone()
    if stored is None:
        return None
    return bytes(stored[0])


def _save_metadata(db: sqlite3.Connection, name: str, content: bytes):
    """Set a metadata value within the caller's transaction.

    Arguments:
        db: review database connection
        name: metadata key
        content: value to store
    """
    db.execute("INSERT OR REPLACE INTO review_metadata VALUES (?, ?)", (name, content))
