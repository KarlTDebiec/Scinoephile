#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.file.get_temp_file_path."""

from __future__ import annotations

from pathlib import Path

from common.file import get_temp_file_path
from pytest import raises


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
    assert temp_file is not None
    assert not temp_file.exists()


def test_get_temp_file_path_with_suffix():
    """Test temporary file path with suffix."""
    with get_temp_file_path(suffix=".txt") as temp_file_path:
        assert temp_file_path.suffix == ".txt"
        assert not temp_file_path.exists()
        assert temp_file_path.is_absolute()


def test_get_temp_file_path_cleanup_on_exception(tmp_path: Path):
    """Test temporary file cleanup even when exception occurs.

    Arguments:
        tmp_path: directory in which to create the temporary file
    Raises:
        ValueError: if a value is invalid
    """
    temp_file = None
    with raises(ValueError, match="Test exception"):
        with get_temp_file_path(parent_dir_path=tmp_path) as temp_file_path:
            temp_file = temp_file_path
            temp_file_path.write_text("test content")
            assert temp_file_path.exists()
            raise ValueError("Test exception")

    # File should still be cleaned up
    assert temp_file is not None
    assert not temp_file.exists()
    assert list(tmp_path.iterdir()) == []


def test_get_temp_file_path_in_parent_directory(tmp_path: Path):
    """Create an absent temporary path on the requested output filesystem.

    Arguments:
        tmp_path: directory in which to create the output directory
    """
    output_dir_path = tmp_path / "output"
    output_dir_path.mkdir()
    existing_file_path = output_dir_path / "existing.txt"
    existing_file_path.write_text("keep", encoding="utf-8")

    with get_temp_file_path(".png", parent_dir_path=output_dir_path) as temp_file_path:
        assert temp_file_path.parent == output_dir_path
        assert temp_file_path.suffix == ".png"
        assert temp_file_path.is_absolute()
        assert not temp_file_path.exists()
        temp_file_path.write_bytes(b"temporary output")

    assert not temp_file_path.exists()
    assert existing_file_path.read_text(encoding="utf-8") == "keep"
    assert list(output_dir_path.iterdir()) == [existing_file_path]


def test_get_temp_file_path_requires_existing_parent(tmp_path: Path):
    """Reject missing parents without creating directories or leaving artifacts.

    Arguments:
        tmp_path: existing ancestor of the missing parent directory
    """
    missing_dir_path = tmp_path / "missing" / "output"
    with raises(FileNotFoundError):
        with get_temp_file_path(parent_dir_path=missing_dir_path):
            pass

    assert not missing_dir_path.exists()
    assert list(tmp_path.iterdir()) == []
