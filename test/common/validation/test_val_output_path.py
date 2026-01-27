#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_output_path."""

from __future__ import annotations

from pathlib import Path

import pytest
from common.validation import val_output_path  # ty:ignore[unresolved-import]


def test_val_output_path_valid(tmp_path: Path):
    """Test validation of valid output path."""
    test_file = tmp_path / "output.txt"

    result = val_output_path(test_file)
    assert isinstance(result, Path)
    assert result.parent.exists()


def test_val_output_path_from_string(tmp_path: Path):
    """Test validation of output path from string."""
    test_file = tmp_path / "output.txt"

    result = val_output_path(str(test_file))
    assert isinstance(result, Path)
    assert result.parent.exists()


def test_val_output_path_creates_parent_dir(tmp_path: Path):
    """Test that parent directory is created if it doesn't exist."""
    test_file = tmp_path / "subdir" / "output.txt"

    result = val_output_path(test_file)
    assert result.parent.exists()
    assert result.parent.is_dir()


def test_val_output_path_nested_parent_dirs(tmp_path: Path):
    """Test that nested parent directories are created."""
    test_file = tmp_path / "dir1" / "dir2" / "dir3" / "output.txt"

    result = val_output_path(test_file)
    assert result.parent.exists()
    assert result.parent.is_dir()


def test_val_output_path_exists_not_ok(tmp_path: Path):
    """Test validation when file exists and exist_ok is False."""
    test_file = tmp_path / "output.txt"
    test_file.write_text("existing content")

    with pytest.raises(FileExistsError):
        val_output_path(test_file, exist_ok=False)


def test_val_output_path_exists_ok(tmp_path: Path):
    """Test validation when file exists and exist_ok is True."""
    test_file = tmp_path / "output.txt"
    test_file.write_text("existing content")

    result = val_output_path(test_file, exist_ok=True)
    assert isinstance(result, Path)
    assert result.exists()


def test_val_output_path_absolute(tmp_path: Path):
    """Test that returned path is absolute."""
    test_file = tmp_path / "output.txt"

    result = val_output_path(test_file)
    assert result.is_absolute()


def test_val_output_path_list_valid(tmp_path: Path):
    """Test validation of list of valid output paths."""
    files = [tmp_path / f"output{i}.txt" for i in range(3)]

    result = val_output_path(files)
    assert isinstance(result, list)
    assert len(result) == 3
    assert all(isinstance(p, Path) for p in result)
    assert all(p.parent.exists() for p in result)


def test_val_output_path_list_empty():
    """Test validation of empty list."""
    result = val_output_path([])
    assert result == []


def test_val_output_path_list_with_existing(tmp_path: Path):
    """Test validation of list with existing file and exist_ok False."""
    test_file1 = tmp_path / "output1.txt"
    test_file2 = tmp_path / "output2.txt"
    test_file2.write_text("existing content")

    with pytest.raises(FileExistsError):
        val_output_path([test_file1, test_file2], exist_ok=False)


def test_val_output_path_list_with_existing_ok(tmp_path: Path):
    """Test validation of list with existing file and exist_ok True."""
    test_file1 = tmp_path / "output1.txt"
    test_file2 = tmp_path / "output2.txt"
    test_file2.write_text("existing content")

    result = val_output_path([test_file1, test_file2], exist_ok=True)
    assert len(result) == 2


def test_val_output_path_tuple(tmp_path: Path):
    """Test validation of tuple of output paths."""
    files = tuple([tmp_path / f"output{i}.txt" for i in range(2)])

    result = val_output_path(files)
    assert isinstance(result, list)
    assert len(result) == 2


def test_val_output_path_expands_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that path expands ~ user directory."""

    # Mock expanduser to return our test path
    def mock_expanduser(path: str) -> str:
        if path.startswith("~"):
            return str(tmp_path / "output.txt")
        return path

    monkeypatch.setattr("common.validation.expanduser", mock_expanduser)

    result = val_output_path("~/output.txt")
    assert result.parent.exists()


def test_val_output_path_expands_vars(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Test that path expands environment variables."""
    monkeypatch.setenv("OUTPUT_FILE", str(tmp_path / "output.txt"))

    result = val_output_path("$OUTPUT_FILE")
    assert result.parent.exists()


def test_val_output_path_default_exist_ok_false(tmp_path: Path):
    """Test that default exist_ok is False."""
    test_file = tmp_path / "output.txt"
    test_file.write_text("existing content")

    with pytest.raises(FileExistsError):
        val_output_path(test_file)
