#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_output_path."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch, raises

from scinoephile.common.exceptions import NotAFileError
from scinoephile.common.validation import val_output_path


def test_val_output_path_accepts_path_values_and_creates_parents(tmp_path: Path):
    """Test output file validation accepts path values and creates parents."""
    file_path = tmp_path / "subdir" / "output.txt"

    assert val_output_path(file_path) == file_path.resolve()
    assert file_path.parent.is_dir()
    assert val_output_path(str(tmp_path / "other.txt")) == (tmp_path / "other.txt")


def test_val_output_path_respects_create_and_exist_ok(tmp_path: Path):
    """Test output file validation respects creation and overwrite options."""
    file_path = tmp_path / "output.txt"
    file_path.write_text("existing content", encoding="utf-8")
    nested_path = tmp_path / "missing" / "output.txt"

    with raises(FileExistsError):
        val_output_path(file_path)
    assert val_output_path(file_path, exist_ok=True) == file_path.resolve()
    assert val_output_path(nested_path, create=False) == nested_path.resolve()
    assert not nested_path.parent.exists()


def test_val_output_path_rejects_directories(tmp_path: Path):
    """Test output file validation rejects directory paths."""
    with raises(NotAFileError):
        val_output_path(tmp_path, exist_ok=True)


def test_val_output_path_handles_iterables(tmp_path: Path):
    """Test output file validation handles iterable values."""
    file_paths = [tmp_path / f"output{idx}.txt" for idx in range(2)]
    existing_path = tmp_path / "existing.txt"
    existing_path.write_text("existing content", encoding="utf-8")

    assert val_output_path(file_paths) == [
        file_path.resolve() for file_path in file_paths
    ]
    assert val_output_path(tuple(file_paths), exist_ok=True) == [
        file_path.resolve() for file_path in file_paths
    ]
    assert val_output_path([]) == []

    with raises(FileExistsError):
        val_output_path([file_paths[0], existing_path])


def test_val_output_path_expands_environment_variables(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test output file validation expands environment variables."""
    file_path = tmp_path / "output.txt"
    monkeypatch.setenv("OUTPUT_FILE", str(file_path))

    assert val_output_path("$OUTPUT_FILE") == file_path.resolve()
