#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.file.get_temp_directory_path."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.common.file import get_temp_directory_path


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


def test_get_temp_directory_path_custom_parent_cleanup_on_error(tmp_path: Path):
    """Test custom location and prefix with cleanup after an exception.

    Arguments:
        tmp_path: pytest temporary directory path
    Raises:
        RuntimeError: to simulate a failure inside the temporary directory context
    """
    unrelated_path = tmp_path / "notes.txt"
    unrelated_path.write_text("keep", encoding="utf-8")

    with raises(RuntimeError, match="failed"):
        with get_temp_directory_path(
            parent_dir_path=tmp_path, prefix=".audio_output."
        ) as temp_dir_path:
            assert temp_dir_path.parent == tmp_path.resolve()
            assert temp_dir_path.name.startswith(".audio_output.")
            (temp_dir_path / "partial.wav").write_bytes(b"partial")
            raise RuntimeError("failed")

    assert not temp_dir_path.exists()
    assert unrelated_path.read_text(encoding="utf-8") == "keep"
