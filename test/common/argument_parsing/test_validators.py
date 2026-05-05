#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.argument_parsing."""

from __future__ import annotations

from argparse import ArgumentTypeError
from pathlib import Path

import pytest

from scinoephile.common.argument_parsing import (
    float_arg,
    input_dir_arg,
    input_file_arg,
    int_arg,
    output_dir_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exceptions import DirectoryNotFoundError


def test_float_arg():
    """Test float_arg validator."""
    validator = float_arg(min_value=0.0, max_value=10.0)

    assert validator("5.5") == 5.5

    with pytest.raises(ArgumentTypeError, match="less than minimum value"):
        validator("-1.0")


def test_int_arg():
    """Test int_arg validator."""
    validator = int_arg(min_value=0, max_value=10)

    assert validator("5") == 5

    with pytest.raises(ArgumentTypeError, match="less than minimum value"):
        validator("-1")


def test_str_arg():
    """Test str_arg validator."""
    validator = str_arg(options=["option1", "option2", "option3"])

    assert validator("option1") == "option1"
    assert validator("OPTION1") == "option1"

    with pytest.raises(ArgumentTypeError, match="is not one of options"):
        validator("invalid")


def test_input_file_arg(tmp_path: Path):
    """Test input_file_arg validator."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    validator = input_file_arg()

    result = validator(str(test_file))
    assert isinstance(result, Path)
    assert result.exists()

    # FileNotFoundError is not caught by get_validator
    with pytest.raises(FileNotFoundError):
        validator(str(tmp_path / "nonexistent.txt"))


def test_input_dir_arg(tmp_path: Path):
    """Test input_dir_arg validator."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    validator = input_dir_arg()

    result = validator(str(test_dir))
    assert isinstance(result, Path)
    assert result.is_dir()

    # DirectoryNotFoundError is not caught by get_validator
    with pytest.raises(DirectoryNotFoundError):
        validator(str(tmp_path / "nonexistent"))


def test_output_file_arg(tmp_path: Path):
    """Test output_file_arg validator."""
    test_file = tmp_path / "output.txt"

    validator = output_file_arg()

    result = validator(str(test_file))
    assert isinstance(result, Path)
    assert result.parent.exists()


def test_output_dir_arg(tmp_path: Path):
    """Test output_dir_arg validator."""
    test_dir = tmp_path / "outputdir"

    validator = output_dir_arg()

    result = validator(str(test_dir))
    assert isinstance(result, Path)
    assert result.exists()
    assert result.is_dir()


def test_output_dir_arg_without_create(tmp_path: Path):
    """Test output_dir_arg validator without directory creation."""
    test_dir = tmp_path / "outputdir"
    assert not test_dir.exists()

    validator = output_dir_arg(create=False)

    result = validator(str(test_dir))
    assert isinstance(result, Path)
    assert result == test_dir.resolve()
    assert not result.exists()


def test_output_dir_arg_without_create_rejects_file_ancestor(tmp_path: Path):
    """Test output_dir_arg rejects paths below a file when create is False."""
    file_path = tmp_path / "parent"
    file_path.write_text("test content")
    test_dir = file_path / "child"

    validator = output_dir_arg(create=False)

    with pytest.raises(NotADirectoryError):
        validator(str(test_dir))
