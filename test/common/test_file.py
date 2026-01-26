#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for file utilities."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.file import (
    get_temp_directory_path,
    get_temp_file_path,
    rename_preexisting_output_path,
)


def test_get_temp_directory_path():
    """Test temporary directory creation and cleanup."""
    temp_dir = None
    with get_temp_directory_path() as temp_directory_path:
        temp_dir = temp_directory_path
        assert temp_directory_path.exists()
        assert temp_directory_path.is_dir()
        assert temp_directory_path.is_absolute()

        # Create a file inside to verify cleanup
        test_file = temp_directory_path / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()

    # After context manager exits, directory should be cleaned up
    assert not temp_dir.exists()


def test_get_temp_file_path_no_suffix():
    """Test temporary file path without suffix."""
    temp_file = None
    with get_temp_file_path() as temp_file_path:
        temp_file = temp_file_path
        # File path is provided but file doesn't exist initially
        assert not temp_file_path.exists()
        assert temp_file_path.is_absolute()

        # Write to the file
        temp_file_path.write_text("test content")
        assert temp_file_path.exists()

    # After context manager exits, file should be cleaned up
    assert not temp_file.exists()


def test_get_temp_file_path_with_suffix():
    """Test temporary file path with suffix."""
    with get_temp_file_path(suffix=".txt") as temp_file_path:
        assert temp_file_path.suffix == ".txt"
        assert not temp_file_path.exists()
        assert temp_file_path.is_absolute()


def test_get_temp_file_path_cleanup_on_exception():
    """Test temporary file cleanup even when exception occurs."""
    temp_file = None
    try:
        with get_temp_file_path() as temp_file_path:
            temp_file = temp_file_path
            temp_file_path.write_text("test content")
            assert temp_file_path.exists()
            raise ValueError("Test exception")
    except ValueError:
        pass

    # File should still be cleaned up
    assert not temp_file.exists()


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
