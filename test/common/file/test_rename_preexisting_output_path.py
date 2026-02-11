#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.file.rename_preexisting_output_path."""

from __future__ import annotations

from typing import TYPE_CHECKING

from common.file import rename_preexisting_output_path  # ty:ignore[unresolved-import]

if TYPE_CHECKING:
    from pathlib import Path


def test_rename_preexisting_output_path_no_existing_file(tmp_path: Path):
    """Test rename when no existing file is present."""
    output_path = tmp_path / "output.txt"

    # Should not raise any errors
    rename_preexisting_output_path(output_path)

    # No files should have been created
    assert not output_path.exists()


def test_rename_preexisting_output_path_single_existing_file(tmp_path: Path):
    """Test rename when a single existing file is present."""
    output_path = tmp_path / "output.txt"
    output_path.write_text("original content")

    rename_preexisting_output_path(output_path)

    # Original file should be moved
    assert not output_path.exists()

    # Backup file should exist
    backup_path = tmp_path / "output_000.txt"
    assert backup_path.exists()
    assert backup_path.read_text() == "original content"


def test_rename_preexisting_output_path_multiple_backups(tmp_path: Path):
    """Test rename when multiple backup files already exist."""
    output_path = tmp_path / "output.txt"

    # Create existing file and backups
    output_path.write_text("latest content")
    (tmp_path / "output_000.txt").write_text("backup 0")
    (tmp_path / "output_001.txt").write_text("backup 1")

    rename_preexisting_output_path(output_path)

    # Original file should be moved to next available backup number
    assert not output_path.exists()

    # All backups should exist
    assert (tmp_path / "output_000.txt").exists()
    assert (tmp_path / "output_001.txt").exists()
    backup_path = tmp_path / "output_002.txt"
    assert backup_path.exists()
    assert backup_path.read_text() == "latest content"


def test_rename_preexisting_output_path_preserves_extension(tmp_path: Path):
    """Test that file extension is preserved during rename."""
    output_path = tmp_path / "output.json"
    output_path.write_text('{"test": "data"}')

    rename_preexisting_output_path(output_path)

    backup_path = tmp_path / "output_000.json"
    assert backup_path.exists()
    assert backup_path.suffix == ".json"


def test_rename_preexisting_output_path_resolves_path(tmp_path: Path):
    """Test that relative paths are resolved."""
    output_path = tmp_path / "subdir" / ".." / "output.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("content")

    # Should work with non-canonical path
    rename_preexisting_output_path(output_path)

    # Backup should be created at resolved location
    resolved_backup = tmp_path / "output_000.txt"
    assert resolved_backup.exists()
