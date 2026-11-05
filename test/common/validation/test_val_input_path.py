#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_input_path."""

from __future__ import annotations

from pathlib import Path

from common.exceptions import NotAFileError
from common.validation import val_input_path
from common_test_support import create_symlink_or_skip
from pytest import MonkeyPatch, raises


def test_val_input_path_accepts_file_path_values(tmp_path: Path):
    """Test input file validation accepts Path and string values.

    Arguments:
        tmp_path: temporary directory path
    """
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content", encoding="utf-8")

    assert val_input_path(file_path) == file_path.resolve()
    assert val_input_path(str(file_path)) == file_path.resolve()


def test_val_input_path_allows_missing_paths(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Allow missing input paths when callers opt in.

    Arguments:
        tmp_path: temporary directory for existing and missing paths
        monkeypatch: fixture for isolating the working directory and environment
    """
    existing_path = tmp_path / "present.txt"
    existing_path.touch()
    missing_path = tmp_path / "missing" / "%06d.png"
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TEST_INPUT_ROOT", str(tmp_path))

    assert val_input_path("missing/%06d.png", must_exist=False) == missing_path
    assert (
        val_input_path("$TEST_INPUT_ROOT/missing/%06d.png", must_exist=False)
        == missing_path
    )
    assert val_input_path([existing_path, missing_path], must_exist=False) == [
        existing_path,
        missing_path,
    ]
    assert not missing_path.parent.exists()
    with raises(NotAFileError):
        val_input_path(tmp_path, must_exist=False)


def test_val_input_path_rejects_missing_and_directory_paths(tmp_path: Path):
    """Test input file validation rejects missing paths and directories.

    Arguments:
        tmp_path: temporary directory path
    """
    dir_path = tmp_path / "testdir"
    dir_path.mkdir()

    with raises(FileNotFoundError):
        val_input_path(tmp_path / "missing.txt")
    with raises(NotAFileError):
        val_input_path(dir_path)


def test_val_input_path_handles_iterables(tmp_path: Path):
    """Test input file validation handles iterable values.

    Arguments:
        tmp_path: temporary directory path
    """
    file_paths = [tmp_path / f"test{idx}.txt" for idx in range(2)]
    for file_path in file_paths:
        file_path.write_text("test content", encoding="utf-8")

    assert val_input_path(file_paths) == [
        file_path.resolve() for file_path in file_paths
    ]
    assert val_input_path(tuple(file_paths)) == [
        file_path.resolve() for file_path in file_paths
    ]
    assert val_input_path([]) == []

    with raises(FileNotFoundError):
        val_input_path([file_paths[0], tmp_path / "missing.txt"])
    with raises(NotAFileError):
        val_input_path([file_paths[0], tmp_path])


def test_val_input_path_expands_and_resolves_paths(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test input file validation expands variables and resolves symlinks.

    Arguments:
        tmp_path: temporary directory path
        monkeypatch: pytest monkeypatch fixture
    """
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content", encoding="utf-8")
    symlink_path = tmp_path / "link.txt"
    create_symlink_or_skip(symlink_path, file_path)
    monkeypatch.setenv("TEST_FILE", str(symlink_path))

    assert val_input_path("$TEST_FILE") == file_path.resolve()
