#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of custom string path-like values in common validation."""

from __future__ import annotations

from os import PathLike
from pathlib import Path

from scinoephile.common.validation import (
    val_child_path,
    val_input_dir_path,
    val_input_file_or_dir_path,
    val_input_path,
    val_output_dir_path,
    val_output_path,
)


class _CustomPath(PathLike[str]):
    """Custom string path-like value used to exercise the public contract."""

    def __init__(self, path: Path):
        """Initialize.

        Arguments:
            path: path represented by this value
        """
        self.path = path

    def __fspath__(self) -> str:
        """Return the filesystem representation.

        Returns:
            string filesystem path
        """
        return str(self.path)


def test_path_validators_accept_custom_string_pathlike(tmp_path: Path):
    """Test path validators accept custom string path-like values.

    Arguments:
        tmp_path: pytest temporary directory path
    """
    input_path = tmp_path / "input.txt"
    input_path.touch()
    output_dir_path = tmp_path / "output"
    output_path = tmp_path / "nested" / "output.txt"

    assert (
        val_child_path(_CustomPath(tmp_path), "child.txt")
        == (tmp_path / "child.txt").resolve()
    )
    assert val_input_dir_path(_CustomPath(tmp_path)) == tmp_path.resolve()
    assert val_input_file_or_dir_path(_CustomPath(input_path)) == input_path.resolve()
    assert val_input_path(_CustomPath(input_path)) == input_path.resolve()
    assert (
        val_output_dir_path(_CustomPath(output_dir_path)) == output_dir_path.resolve()
    )
    assert val_output_path(_CustomPath(output_path)) == output_path.resolve()
