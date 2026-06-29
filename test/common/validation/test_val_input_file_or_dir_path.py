#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_input_file_or_dir_path."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.common.validation import val_input_file_or_dir_path
from test.helpers import create_symlink_or_skip


def test_val_input_file_or_dir_path_accepts_file(tmp_path: Path):
    """Test input file-or-directory path validation accepts a file."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")

    result = val_input_file_or_dir_path(file_path)

    assert result == file_path.resolve()


def test_val_input_file_or_dir_path_accepts_directory(tmp_path: Path):
    """Test input file-or-directory path validation accepts a directory."""
    dir_path = tmp_path / "testdir"
    dir_path.mkdir()

    result = val_input_file_or_dir_path(str(dir_path))

    assert result == dir_path.resolve()


def test_val_input_file_or_dir_path_rejects_missing_path(tmp_path: Path):
    """Test input file-or-directory path validation rejects a missing path."""
    with raises(FileNotFoundError):
        val_input_file_or_dir_path(tmp_path / "missing")


def test_val_input_file_or_dir_path_resolves_symlink(tmp_path: Path):
    """Test input file-or-directory path validation resolves symlinks."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")
    symlink_path = tmp_path / "link.txt"
    create_symlink_or_skip(symlink_path, file_path)

    result = val_input_file_or_dir_path(symlink_path)

    assert result == file_path.resolve()
