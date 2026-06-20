#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.argument_parsing.get_validator."""

from __future__ import annotations

from argparse import ArgumentTypeError

from pytest import raises

from scinoephile.common.argument_parsing import get_validator


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

    with raises(ArgumentTypeError):
        validator("test")


def test_get_validator_os_error():
    """Test get_validator converts OSError to ArgumentTypeError."""

    def failing_func(value: str) -> str:
        """Function that raises OSError.

        Arguments:
            value: input value
        Returns:
            validated value
        Raises:
            OSError: always
        """
        raise OSError("Invalid path")

    validator = get_validator(failing_func)

    with raises(ArgumentTypeError, match="Invalid path"):
        validator("test")
