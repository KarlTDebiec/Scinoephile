#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_literal."""

from __future__ import annotations

from typing import Literal

import pytest
from common.exception import ArgumentConflictError  # ty:ignore[unresolved-import]
from common.validation import val_literal  # ty:ignore[unresolved-import]

type Color = Literal["red", "green", "blue"]
type Level = Literal[1, 2, 3]


def test_val_literal_literal_type_valid():
    """Test validation against a Literal type."""
    assert val_literal("green", Literal["red", "green", "blue"]) == "green"


def test_val_literal_non_literal():
    """Test validation with non-Literal type."""
    with pytest.raises(ArgumentConflictError, match="does not contain Literal options"):
        val_literal("red", str)


def test_val_literal_type_alias_invalid():
    """Test validation with invalid value against a type alias."""
    with pytest.raises(ValueError, match="not one of options"):
        val_literal("yellow", Color)


def test_val_literal_type_alias_valid_int():
    """Test validation of a valid int against a type alias."""
    assert val_literal(2, Level) == 2


def test_val_literal_type_alias_valid_str():
    """Test validation of a valid str against a type alias."""
    assert val_literal("red", Color) == "red"
