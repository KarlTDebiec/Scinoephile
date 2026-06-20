#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_input_dir_path."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch, raises

from scinoephile.common.exceptions import DirectoryNotFoundError
from scinoephile.common.validation import val_input_dir_path
from test.helpers import create_symlink_or_skip


def test_val_input_dir_path_accepts_directory_path_values(tmp_path: Path):
    """Test input directory validation accepts Path and string values."""
    dir_path = tmp_path / "testdir"
    dir_path.mkdir()

    assert val_input_dir_path(dir_path) == dir_path.resolve()
    assert val_input_dir_path(str(dir_path)) == dir_path.resolve()


def test_val_input_dir_path_rejects_missing_and_file_paths(tmp_path: Path):
    """Test input directory validation rejects missing paths and files."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content", encoding="utf-8")

    with raises(DirectoryNotFoundError):
        val_input_dir_path(tmp_path / "missing")
    with raises(NotADirectoryError):
        val_input_dir_path(file_path)


def test_val_input_dir_path_handles_iterables(tmp_path: Path):
    """Test input directory validation handles iterable values."""
    dir_paths = [tmp_path / f"testdir{idx}" for idx in range(2)]
    for dir_path in dir_paths:
        dir_path.mkdir()
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content", encoding="utf-8")

    assert val_input_dir_path(dir_paths) == [
        dir_path.resolve() for dir_path in dir_paths
    ]
    assert val_input_dir_path(tuple(dir_paths)) == [
        dir_path.resolve() for dir_path in dir_paths
    ]
    assert val_input_dir_path([]) == []

    with raises(DirectoryNotFoundError):
        val_input_dir_path([dir_paths[0], tmp_path / "missing"])
    with raises(NotADirectoryError):
        val_input_dir_path([dir_paths[0], file_path])


def test_val_input_dir_path_expands_and_resolves_paths(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test input directory validation expands variables and resolves symlinks."""
    dir_path = tmp_path / "testdir"
    dir_path.mkdir()
    symlink_path = tmp_path / "linkdir"
    create_symlink_or_skip(symlink_path, dir_path, target_is_directory=True)
    monkeypatch.setenv("TEST_DIR", str(symlink_path))

    assert val_input_dir_path("$TEST_DIR") == dir_path.resolve()
