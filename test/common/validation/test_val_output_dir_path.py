#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_output_dir_path."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch, raises

from scinoephile.common.validation import val_output_dir_path


def test_val_output_dir_path_accepts_path_values_and_creates_directories(
    tmp_path: Path,
):
    """Test output directory validation accepts path values and creates directories."""
    dir_path = tmp_path / "outputdir"
    string_dir_path = tmp_path / "stringdir"

    assert val_output_dir_path(dir_path) == dir_path.resolve()
    assert dir_path.is_dir()
    assert val_output_dir_path(str(string_dir_path)) == string_dir_path.resolve()
    assert string_dir_path.is_dir()


def test_val_output_dir_path_respects_create_option(tmp_path: Path):
    """Test output directory validation respects the create option."""
    dir_path = tmp_path / "newdir"
    file_path = tmp_path / "parent"
    file_path.write_text("test content", encoding="utf-8")

    assert val_output_dir_path(dir_path, create=False) == dir_path.resolve()
    assert not dir_path.exists()
    with raises(NotADirectoryError):
        val_output_dir_path(file_path / "child", create=False)


def test_val_output_dir_path_rejects_file_paths(tmp_path: Path):
    """Test output directory validation rejects file paths."""
    file_path = tmp_path / "output.txt"
    file_path.write_text("test content", encoding="utf-8")

    with raises(NotADirectoryError):
        val_output_dir_path(file_path)


def test_val_output_dir_path_handles_iterables(tmp_path: Path):
    """Test output directory validation handles iterable values."""
    existing_dir_path = tmp_path / "existingdir"
    existing_dir_path.mkdir()
    new_dir_path = tmp_path / "newdir"
    file_path = tmp_path / "output.txt"
    file_path.write_text("test content", encoding="utf-8")

    assert val_output_dir_path([existing_dir_path, new_dir_path]) == [
        existing_dir_path.resolve(),
        new_dir_path.resolve(),
    ]
    assert existing_dir_path.is_dir()
    assert new_dir_path.is_dir()
    assert val_output_dir_path(()) == []

    with raises(NotADirectoryError):
        val_output_dir_path([existing_dir_path, file_path])


def test_val_output_dir_path_expands_environment_variables(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test output directory validation expands environment variables."""
    dir_path = tmp_path / "outputdir"
    monkeypatch.setenv("OUTPUT_DIR", str(dir_path))

    assert val_output_dir_path("$OUTPUT_DIR") == dir_path.resolve()
    assert dir_path.is_dir()
