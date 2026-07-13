#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_child_path."""

from __future__ import annotations

from pathlib import Path

from pytest import param, raises

from scinoephile.common.validation import val_child_path
from test.helpers import create_symlink_or_skip, parametrize


def test_val_child_path_accepts_contained_filename(tmp_path: Path):
    """Test child path validation accepts a contained filename.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    parent_dir_path = tmp_path / "parent"
    parent_dir_path.mkdir()

    assert (
        val_child_path(parent_dir_path, "eng-2.srt")
        == (parent_dir_path / "eng-2.srt").resolve()
    )


@parametrize(
    "child_name",
    [
        param("", id="empty"),
        param(".", id="current-directory"),
        param("..", id="parent-directory"),
        param("../outside.srt", id="posix-parent"),
        param("nested/outside.srt", id="posix-nested"),
        param("/outside.srt", id="posix-absolute"),
        param(r"..\outside.srt", id="windows-parent"),
        param(r"nested\outside.srt", id="windows-nested"),
        param(r"C:\outside.srt", id="windows-absolute"),
    ],
)
def test_val_child_path_rejects_non_filename_components(
    child_name: str,
    tmp_path: Path,
):
    """Test child path validation rejects paths and special components.

    Arguments:
        child_name: proposed child name
        tmp_path: pytest temporary directory path
    """
    with raises(ValueError, match="single contained filename"):
        val_child_path(tmp_path, child_name)


def test_val_child_path_rejects_symlink_outside_parent(tmp_path: Path):
    """Test child path validation rejects symlinks outside the parent.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    parent_dir_path = tmp_path / "parent"
    parent_dir_path.mkdir()
    outside_path = tmp_path / "outside.srt"
    outside_path.touch()
    symlink_path = parent_dir_path / "linked.srt"
    create_symlink_or_skip(symlink_path, outside_path)

    with raises(ValueError, match="single contained filename"):
        val_child_path(parent_dir_path, symlink_path.name)
