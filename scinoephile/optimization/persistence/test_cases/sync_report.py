#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Data model for test case sync results."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ["SyncReport"]


@dataclass(frozen=True, slots=True)
class SyncReport:
    """Summary of a sync operation."""

    table_name: str
    """SQLite table name that was synchronized."""
    input_paths: tuple[Path, ...]
    """Input JSON paths included in the sync run."""
    insert_ids: tuple[str, ...]
    """Test case identifiers that would be inserted/updated."""
    delete_ids: tuple[str, ...]
    """Test case identifiers whose link to an input path would be removed."""
