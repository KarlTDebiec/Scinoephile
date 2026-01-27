#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_output_dir_path."""

from __future__ import annotations

from pathlib import Path

import pytest
from common.validation import val_output_dir_path  # ty:ignore[unresolved-import]


def test_val_output_dir_path_valid(tmp_path: Path):
    """Test validation of valid output directory path."""
    test_dir = tmp_path / "outputdir"

    result = val_output_dir_path(test_dir)
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()


def test_val_output_dir_path_from_string(tmp_path: Path):
    """Test validation of output directory path from string."""
    test_dir = tmp_path / "outputdir"

    result = val_output_dir_path(str(test_dir))
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()


def test_val_output_dir_path_creates_dir(tmp_path: Path):
    """Test that directory is created if it doesn't exist."""
    test_dir = tmp_path / "newdir"
    assert not test_dir.exists()

    result = val_output_dir_path(test_dir)
    assert result.exists()
    assert result.is_dir()


def test_val_output_dir_path_nested_dirs(tmp_path: Path):
    """Test that nested directories are created."""
    test_dir = tmp_path / "dir1" / "dir2" / "dir3"
    assert not test_dir.exists()

    result = val_output_dir_path(test_dir)
    assert result.exists()
    assert result.is_dir()


def test_val_output_dir_path_already_exists(tmp_path: Path):
    """Test validation when directory already exists."""
    test_dir = tmp_path / "outputdir"
    test_dir.mkdir()

    result = val_output_dir_path(test_dir)
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()


def test_val_output_dir_path_not_a_directory(tmp_path: Path):
    """Test validation when path exists but is not a directory."""
    test_file = tmp_path / "output.txt"
    test_file.write_text("test content")

    with pytest.raises(NotADirectoryError):
        val_output_dir_path(test_file)


def test_val_output_dir_path_absolute(tmp_path: Path):
    """Test that returned path is absolute."""
    test_dir = tmp_path / "outputdir"

    result = val_output_dir_path(test_dir)
    assert result.is_absolute()


def test_val_output_dir_path_list_valid(tmp_path: Path):
    """Test validation of list of valid output directory paths."""
    dirs = [tmp_path / f"outputdir{i}" for i in range(3)]

    result = val_output_dir_path(dirs)
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(p, Path) for p in result)
    assert all(p.exists() and p.is_dir() for p in result)


def test_val_output_dir_path_list_empty():
    """Test validation of empty list."""
    result = val_output_dir_path([])
    assert result == []


def test_val_output_dir_path_list_with_file(tmp_path: Path):
    """Test validation of list with a file path."""
    test_dir = tmp_path / "outputdir"
    test_file = tmp_path / "output.txt"
    test_file.write_text("test content")

    with pytest.raises(NotADirectoryError):
        val_output_dir_path([test_dir, test_file])


def test_val_output_dir_path_tuple(tmp_path: Path):
    """Test validation of tuple of output directory paths."""
    dirs = tuple([tmp_path / f"outputdir{i}" for i in range(2)])

    result = val_output_dir_path(dirs)
    assert isinstance(result, list)
    assert len(result) == 2
    assert all(p.exists() and p.is_dir() for p in result)


def test_val_output_dir_path_expands_user(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that path expands ~ user directory."""

    # Mock expanduser to return our test path
    def mock_expanduser(path: str) -> str:
        if path.startswith("~"):
            return str(tmp_path / "outputdir")
        return path

    monkeypatch.setattr("common.validation.expanduser", mock_expanduser)

    result = val_output_dir_path("~/outputdir")
    assert result.exists()
    assert result.is_dir()


def test_val_output_dir_path_expands_vars(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test that path expands environment variables."""
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "outputdir"))

    result = val_output_dir_path("$OUTPUT_DIR")
    assert result.exists()
    assert result.is_dir()


def test_val_output_dir_path_list_mixed(tmp_path: Path):
    """Test validation of list with existing and non-existing directories."""
    test_dir1 = tmp_path / "existingdir"
    test_dir1.mkdir()

    test_dir2 = tmp_path / "newdir"

    result = val_output_dir_path([test_dir1, test_dir2])
    assert len(result) == 2
    assert all(p.exists() and p.is_dir() for p in result)
