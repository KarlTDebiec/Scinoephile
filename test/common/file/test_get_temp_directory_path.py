#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.file.get_temp_directory_path."""

from __future__ import annotations

from common.file import get_temp_directory_path  # ty:ignore[unresolved-import]


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
