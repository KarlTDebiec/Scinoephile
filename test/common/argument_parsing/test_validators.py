#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.argument_parsing."""

from __future__ import annotations

from argparse import ArgumentTypeError
from pathlib import Path

from pytest import raises

from scinoephile.common.argument_parsing import (
    duration_arg,
    float_arg,
    input_dir_arg,
    input_file_arg,
    input_file_or_dir_arg,
    int_arg,
    output_dir_arg,
    output_file_arg,
    str_arg,
)


def test_duration_arg():
    """Test duration_arg validator."""
    validator = duration_arg

    assert validator("12h").total_seconds() == 12 * 60 * 60

    with raises(ArgumentTypeError, match="Invalid duration"):
        validator("yesterday")


def test_float_arg():
    """Test float_arg validator."""
    validator = float_arg(min_value=0.0, max_value=10.0)

    assert validator("5.5") == 5.5

    with raises(ArgumentTypeError, match="less than minimum value"):
        validator("-1.0")


def test_int_arg():
    """Test int_arg validator."""
    validator = int_arg(min_value=0, max_value=10)

    assert validator("5") == 5

    with raises(ArgumentTypeError, match="less than minimum value"):
        validator("-1")


def test_str_arg():
    """Test str_arg validator."""
    validator = str_arg(options=["option1", "option2", "option3"])

    assert validator("option1") == "option1"
    assert validator("OPTION1") == "option1"

    with raises(
        ArgumentTypeError,
        match="'invalid' is not one of the supported values: option1, option2, option3",
    ):
        validator("invalid")


def test_input_file_arg(tmp_path: Path):
    """Test input_file_arg validator."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    validator = input_file_arg()

    result = validator(str(test_file))
    assert isinstance(result, Path)
    assert result.exists()

    with raises(ArgumentTypeError, match="does not exist"):
        validator(str(tmp_path / "nonexistent.txt"))


def test_input_file_or_dir_arg(tmp_path: Path):
    """Test input_file_or_dir_arg validator."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    validator = input_file_or_dir_arg()

    assert validator(str(test_file)) == test_file.resolve()
    assert validator(str(test_dir)) == test_dir.resolve()

    with raises(ArgumentTypeError, match="does not exist"):
        validator(str(tmp_path / "nonexistent"))


def test_input_dir_arg(tmp_path: Path):
    """Test input_dir_arg validator."""
    test_dir = tmp_path / "testdir"
    test_dir.mkdir()

    validator = input_dir_arg()

    result = validator(str(test_dir))
    assert isinstance(result, Path)
    assert result.is_dir()

    with raises(ArgumentTypeError, match="does not exist"):
        validator(str(tmp_path / "nonexistent"))


def test_output_file_arg(tmp_path: Path):
    """Test output_file_arg validator."""
    test_file = tmp_path / "output.txt"

    validator = output_file_arg()

    result = validator(str(test_file))
    assert isinstance(result, Path)
    assert result.parent.exists()


def test_output_file_arg_rejects_existing_file_with_argparse_error(tmp_path: Path):
    """Test output_file_arg reports existing files as argparse errors."""
    test_file = tmp_path / "output.txt"
    test_file.write_text("existing", encoding="utf-8")

    validator = output_file_arg()

    with raises(ArgumentTypeError, match="already exists"):
        validator(str(test_file))


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

    with raises(ArgumentTypeError, match="is not a directory"):
        validator(str(test_dir))
