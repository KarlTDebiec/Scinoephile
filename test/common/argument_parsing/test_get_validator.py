#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.argument_parsing.get_validator."""

from __future__ import annotations

from argparse import ArgumentTypeError

import pytest
from common.argument_parsing import get_validator  # ty:ignore[unresolved-import]


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
