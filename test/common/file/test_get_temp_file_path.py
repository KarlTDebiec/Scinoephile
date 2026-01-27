#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.file.get_temp_file_path."""

from __future__ import annotations

from common.file import get_temp_file_path  # ty:ignore[unresolved-import]


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
    assert temp_file is not None
    assert not temp_file.exists()
