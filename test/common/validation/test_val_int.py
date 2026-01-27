#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_int."""

from __future__ import annotations

import pytest
from common.exception import ArgumentConflictError  # ty:ignore[unresolved-import]
from common.validation import val_int  # ty:ignore[unresolved-import]


def test_val_int_single_valid():
    """Test validation of single valid int."""
    assert val_int(5) == 5
    assert val_int(0) == 0
    assert val_int(-3) == -3


def test_val_int_single_from_float():
    """Test validation of int from float."""
    assert val_int(5.0) == 5
    assert val_int(0.0) == 0
    assert val_int(-3.0) == -3


def test_val_int_single_from_string():
    """Test validation of int from string."""
    assert val_int("5") == 5
    assert val_int("0") == 0
    assert val_int("-3") == -3


def test_val_int_single_invalid_type():
    """Test validation with invalid type."""
    with pytest.raises(TypeError):
        val_int(None)
    with pytest.raises(TypeError):
        val_int("invalid_string")


def test_val_int_single_min_value():
    """Test validation with minimum value constraint."""
    assert val_int(5, min_value=0) == 5
    assert val_int(0, min_value=0) == 0

    with pytest.raises(ValueError, match="less than minimum"):
        val_int(-1, min_value=0)


def test_val_int_single_max_value():
    """Test validation with maximum value constraint."""
    assert val_int(5, max_value=10) == 5
    assert val_int(10, max_value=10) == 10

    with pytest.raises(ValueError, match="greater than maximum"):
        val_int(11, max_value=10)


def test_val_int_single_min_max_value():
    """Test validation with both min and max value constraints."""
    assert val_int(5, min_value=0, max_value=10) == 5
    assert val_int(0, min_value=0, max_value=10) == 0
    assert val_int(10, min_value=0, max_value=10) == 10

    with pytest.raises(ValueError, match="less than minimum"):
        val_int(-1, min_value=0, max_value=10)

    with pytest.raises(ValueError, match="greater than maximum"):
        val_int(11, min_value=0, max_value=10)


def test_val_int_single_acceptable_values():
    """Test validation with acceptable values constraint."""
    assert val_int(1, acceptable_values=[1, 2, 3]) == 1
    assert val_int(2, acceptable_values=[1, 2, 3]) == 2
    assert val_int(3, acceptable_values=[1, 2, 3]) == 3

    with pytest.raises(ValueError, match="is not one of"):
        val_int(4, acceptable_values=[1, 2, 3])


def test_val_int_conflicting_min_max():
    """Test validation with conflicting min and max values."""
    with pytest.raises(ArgumentConflictError, match="min_value must be less than"):
        val_int(5, min_value=10, max_value=5)

    with pytest.raises(ArgumentConflictError):
        val_int(5, min_value=5, max_value=5)


def test_val_int_list_valid():
    """Test validation of list of valid ints."""
    assert val_int([1, 2, 3]) == [1, 2, 3]
    assert val_int([1.0, 2.0, 3.0]) == [1, 2, 3]
    assert val_int(["1", "2", "3"]) == [1, 2, 3]


def test_val_int_list_empty():
    """Test validation of empty list."""
    assert val_int([]) == []


def test_val_int_list_single_element():
    """Test validation of list with single element."""
    assert val_int([5]) == [5]


def test_val_int_list_n_values():
    """Test validation with n_values constraint."""
    assert val_int([1, 2, 3], n_values=3) == [1, 2, 3]

    with pytest.raises(ValueError, match="is of length"):
        val_int([1, 2], n_values=3)

    with pytest.raises(ValueError, match="is of length"):
        val_int([1, 2, 3, 4], n_values=3)


def test_val_int_list_min_value():
    """Test validation of list with minimum value constraint."""
    assert val_int([1, 2, 3], min_value=0) == [1, 2, 3]

    with pytest.raises(ValueError, match="less than minimum"):
        val_int([1, -1, 3], min_value=0)


def test_val_int_list_max_value():
    """Test validation of list with maximum value constraint."""
    assert val_int([1, 2, 3], max_value=10) == [1, 2, 3]

    with pytest.raises(ValueError, match="greater than maximum"):
        val_int([1, 11, 3], max_value=10)


def test_val_int_list_acceptable_values():
    """Test validation of list with acceptable values constraint."""
    assert val_int([1, 2, 3], acceptable_values=[1, 2, 3, 4]) == [1, 2, 3]

    with pytest.raises(ValueError, match="is not one of"):
        val_int([1, 2, 5], acceptable_values=[1, 2, 3, 4])


def test_val_int_list_invalid_type():
    """Test validation of list with invalid element type."""
    with pytest.raises(TypeError):
        val_int([1, None, 3])

    with pytest.raises(TypeError):
        val_int([1, "invalid", 3])


def test_val_int_tuple():
    """Test validation of tuple of ints."""
    assert val_int((1, 2, 3)) == [1, 2, 3]


def test_val_int_generator():
    """Test validation of generator of ints."""
    result = val_int(x for x in [1, 2, 3])
    assert result == [1, 2, 3]
