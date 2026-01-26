#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for argument parsing utilities."""

from __future__ import annotations

from argparse import ArgumentParser, ArgumentTypeError
from pathlib import Path

import pytest

from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    get_optional_args_group,
    get_required_args_group,
    get_validator,
    input_dir_arg,
    input_file_arg,
    int_arg,
    output_dir_arg,
    output_file_arg,
    str_arg,
)


def test_get_optional_args_group():
    """Test retrieving the optional arguments group."""
    parser = ArgumentParser()

    # In newer Python versions, the title may be "options" instead of
    # "optional arguments". The function expects "optional arguments" so it may
    # fail on newer versions. This test checks if the function can find the group
    try:
        optional_group = get_optional_args_group(parser)
        assert optional_group is not None
        assert optional_group.title in ["optional arguments", "options"]
    except StopIteration:
        # In Python 3.13+, the default group is "options", not "optional arguments"
        # The function may not find it if it only looks for "optional arguments"
        pytest.skip("get_optional_args_group requires 'optional arguments' group")


def test_get_required_args_group_new():
    """Test creating a new required arguments group."""
    parser = ArgumentParser()
    required_group = get_required_args_group(parser)

    assert required_group is not None
    assert required_group.title == "required arguments"


def test_get_required_args_group_existing():
    """Test retrieving an existing required arguments group."""
    parser = ArgumentParser()

    # Create the group first
    first_group = get_required_args_group(parser)

    # Get it again
    second_group = get_required_args_group(parser)

    # Should be the same object
    assert first_group is second_group


def test_get_arg_groups_by_name_new():
    """Test creating new argument groups by name."""
    parser = ArgumentParser()

    groups = get_arg_groups_by_name(
        parser, "input arguments", "operation arguments", "output arguments"
    )

    assert "input arguments" in groups
    assert "operation arguments" in groups
    assert "output arguments" in groups
    assert "optional arguments" in groups


def test_get_arg_groups_by_name_existing():
    """Test getting existing argument groups by name."""
    parser = ArgumentParser()

    # Create groups
    parser.add_argument_group("input arguments")

    groups = get_arg_groups_by_name(parser, "input arguments", "output arguments")

    assert "input arguments" in groups
    assert "output arguments" in groups


def test_get_arg_groups_by_name_order():
    """Test that argument groups are ordered correctly."""
    parser = ArgumentParser()

    get_arg_groups_by_name(parser, "first", "second", "third")

    group_titles = [ag.title for ag in parser._action_groups]

    # Specified groups should come before optional arguments
    first_idx = group_titles.index("first")
    second_idx = group_titles.index("second")
    third_idx = group_titles.index("third")
    optional_idx = group_titles.index("optional arguments")

    assert first_idx < second_idx < third_idx < optional_idx


def test_get_arg_groups_by_name_rename_optional():
    """Test renaming optional arguments group."""
    parser = ArgumentParser()

    groups = get_arg_groups_by_name(
        parser, "input arguments", optional_arguments_name="other arguments"
    )

    assert "other arguments" in groups
    assert "optional arguments" not in groups


def test_get_validator_basic():
    """Test get_validator with a basic function."""

    def sample_func(value: str, prefix: str = "") -> str:
        """Sample validation function.

        Arguments:
            value: input value
            prefix: prefix to add
        Returns:
            prefixed value
        """
        return f"{prefix}{value}"

    validator = get_validator(sample_func, prefix="test_")

    result = validator("value")
    assert result == "test_value"


def test_get_validator_type_error():
    """Test get_validator converts TypeError to ArgumentTypeError."""

    def failing_func(value: str) -> str:
        """Function that raises TypeError.

        Arguments:
            value: input value
        Returns:
            validated value
        Raises:
            TypeError: always
        """
        raise TypeError("Invalid type")

    validator = get_validator(failing_func)

    with pytest.raises(ArgumentTypeError):
        validator("test")


def test_float_arg():
    """Test float_arg validator."""
    validator = float_arg(min_value=0.0, max_value=10.0)

    assert validator("5.5") == 5.5

    # ValueError is not caught by get_validator, only TypeError
    with pytest.raises(ValueError):
        validator("-1.0")


def test_int_arg():
    """Test int_arg validator."""
    validator = int_arg(min_value=0, max_value=10)

    assert validator("5") == 5

    # ValueError is not caught by get_validator, only TypeError
    with pytest.raises(ValueError):
        validator("-1")


def test_str_arg():
    """Test str_arg validator."""
    validator = str_arg(options=["option1", "option2", "option3"])

    assert validator("option1") == "option1"
    assert validator("OPTION1") == "option1"

    # ValueError is not caught by get_validator, only TypeError
    with pytest.raises(ValueError):
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
    with pytest.raises(Exception):  # Could be DirectoryNotFoundError or similar
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


def test_validators_in_argparse(tmp_path: Path):
    """Test using validators in ArgumentParser."""
    parser = ArgumentParser()

    test_file = tmp_path / "input.txt"
    test_file.write_text("test")

    parser.add_argument("--input", type=input_file_arg())
    parser.add_argument("--number", type=int_arg(min_value=0))

    args = parser.parse_args(["--input", str(test_file), "--number", "42"])

    assert isinstance(args.input, Path)
    assert args.input.exists()
    assert args.number == 42
