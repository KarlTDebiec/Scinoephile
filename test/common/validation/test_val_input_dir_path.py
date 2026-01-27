#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_input_dir_path."""

from __future__ import annotations

from pathlib import Path

import pytest
from common.exception import DirectoryNotFoundError  # ty:ignore[unresolved-import]
from common.validation import val_input_dir_path  # ty:ignore[unresolved-import]


def test_val_input_dir_path_valid(tmp_path: Path):
    """Test validation of valid input directory path."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    result = val_input_dir_path(test_dir)
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()


def test_val_input_dir_path_from_string(tmp_path: Path):
    """Test validation of input directory path from string."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    result = val_input_dir_path(str(test_dir))
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()


def test_val_input_dir_path_not_found(tmp_path: Path):
    """Test validation of non-existent directory."""
    test_dir = tmp_path / "nonexistent"

    with pytest.raises(DirectoryNotFoundError):
        val_input_dir_path(test_dir)


def test_val_input_dir_path_not_a_directory(tmp_path: Path):
    """Test validation when path is not a directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    with pytest.raises(NotADirectoryError):
        val_input_dir_path(test_file)


def test_val_input_dir_path_absolute(tmp_path: Path):
    """Test that returned path is absolute."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    result = val_input_dir_path(test_dir)
    assert result.is_absolute()


def test_val_input_dir_path_resolves_symlink(tmp_path: Path):
    """Test that path resolves symlinks."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    symlink = tmp_path / "linkdir"
    symlink.symlink_to(test_dir)

    result = val_input_dir_path(symlink)
    assert result == test_dir.resolve()


def test_val_input_dir_path_list_valid(tmp_path: Path):
    """Test validation of list of valid directory paths."""
    dirs = []
    for i in range(3):
        test_dir = tmp_path / f"testdir{i}"
        test_dir.mkdir()
        dirs.append(test_dir)

    result = val_input_dir_path(dirs)
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(p, Path) for p in result)
    assert all(p.exists() and p.is_dir() for p in result)


def test_val_input_dir_path_list_empty():
    """Test validation of empty list."""
    result = val_input_dir_path([])
    assert result == []


def test_val_input_dir_path_list_with_invalid(tmp_path: Path):
    """Test validation of list with one invalid directory."""
    test_dir1 = tmp_path / "testdir1"
    test_dir1.mkdir()

    test_dir2 = tmp_path / "nonexistent"

    with pytest.raises(DirectoryNotFoundError):
        val_input_dir_path([test_dir1, test_dir2])


def test_val_input_dir_path_list_with_file(tmp_path: Path):
    """Test validation of list with a file."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    with pytest.raises(NotADirectoryError):
        val_input_dir_path([test_dir, test_file])


def test_val_input_dir_path_tuple(tmp_path: Path):
    """Test validation of tuple of directory paths."""
    dirs = []
    for i in range(2):
        test_dir = tmp_path / f"testdir{i}"
        test_dir.mkdir()
        dirs.append(test_dir)

    result = val_input_dir_path(tuple(dirs))
    assert isinstance(result, list)
    assert len(result) == 2


def test_val_input_dir_path_expands_user(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that path expands ~ user directory."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    # Mock expanduser to return our test path
    def mock_expanduser(path: str) -> str:
        if path.startswith("~"):
            return str(test_dir)
        return path

    monkeypatch.setattr("common.validation.expanduser", mock_expanduser)

    result = val_input_dir_path("~/testdir")
    assert result.exists()


def test_val_input_dir_path_expands_vars(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that path expands environment variables."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    monkeypatch.setenv("TEST_DIR", str(test_dir))

    result = val_input_dir_path("$TEST_DIR")
    assert result.exists()
    assert result.is_dir()
