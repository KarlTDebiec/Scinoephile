#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_input_path."""

from __future__ import annotations

from pathlib import Path

import pytest
from common.exception import NotAFileError  # ty:ignore[unresolved-import]
from common.validation import val_input_path  # ty:ignore[unresolved-import]


def test_val_input_path_valid(tmp_path: Path):
    """Test validation of valid input path."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    result = val_input_path(test_file)
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_file()


def test_val_input_path_from_string(tmp_path: Path):
    """Test validation of input path from string."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    result = val_input_path(str(test_file))
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_file()


def test_val_input_path_not_found(tmp_path: Path):
    """Test validation of non-existent path."""
    test_file = tmp_path / "nonexistent.txt"

    with pytest.raises(FileNotFoundError):
        val_input_path(test_file)


def test_val_input_path_not_a_file(tmp_path: Path):
    """Test validation when path is not a file."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    with pytest.raises(NotAFileError):
        val_input_path(test_dir)


def test_val_input_path_absolute(tmp_path: Path):
    """Test that returned path is absolute."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    result = val_input_path(test_file)
    assert result.is_absolute()


def test_val_input_path_resolves_symlink(tmp_path: Path):
    """Test that path resolves symlinks."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    symlink = tmp_path / "link.txt"
    symlink.symlink_to(test_file)

    result = val_input_path(symlink)
    assert result == test_file.resolve()


def test_val_input_path_list_valid(tmp_path: Path):
    """Test validation of list of valid paths."""
    files = []
    for i in range(3):
        test_file = tmp_path / f"test{i}.txt"
        test_file.write_text(f"test content {i}")
        files.append(test_file)

    result = val_input_path(files)
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(p, Path) for p in result)
    assert all(p.exists() and p.is_file() for p in result)


def test_val_input_path_list_empty():
    """Test validation of empty list."""
    result = val_input_path([])
    assert result == []


def test_val_input_path_list_with_invalid(tmp_path: Path):
    """Test validation of list with one invalid path."""
    test_file1 = tmp_path / "test1.txt"
    test_file1.write_text("test content 1")

    test_file2 = tmp_path / "nonexistent.txt"

    with pytest.raises(FileNotFoundError):
        val_input_path([test_file1, test_file2])


def test_val_input_path_list_with_directory(tmp_path: Path):
    """Test validation of list with a directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    with pytest.raises(NotAFileError):
        val_input_path([test_file, test_dir])


def test_val_input_path_tuple(tmp_path: Path):
    """Test validation of tuple of paths."""
    files = []
    for i in range(2):
        test_file = tmp_path / f"test{i}.txt"
        test_file.write_text(f"test content {i}")
        files.append(test_file)

    result = val_input_path(tuple(files))
    assert isinstance(result, list)
    assert len(result) == 2


def test_val_input_path_expands_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that path expands ~ user directory."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Mock expanduser to return our test path
    def mock_expanduser(path: str) -> str:
        if path.startswith("~"):
            return str(test_file)
        return path

    monkeypatch.setattr("common.validation.expanduser", mock_expanduser)

    result = val_input_path("~/test.txt")
    assert result.exists()


def test_val_input_path_expands_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that path expands environment variables."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    monkeypatch.setenv("TEST_FILE", str(test_file))

    result = val_input_path("$TEST_FILE")
    assert result.exists()
    assert result.is_file()
