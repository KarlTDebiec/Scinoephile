#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_float."""

from __future__ import annotations

import pytest
from common.exception import ArgumentConflictError  # ty:ignore[unresolved-import]
from common.validation import val_float  # ty:ignore[unresolved-import]


def test_val_float_single_valid():
    """Test validation of single valid float."""
    assert val_float(3.14) == 3.14
    assert val_float(0.0) == 0.0
    assert val_float(-1.5) == -1.5


def test_val_float_single_from_int():
    """Test validation of float from int."""
    assert val_float(5) == 5.0
    assert val_float(0) == 0.0
    assert val_float(-3) == -3.0


def test_val_float_single_from_string():
    """Test validation of float from string."""
    assert val_float("3.14") == 3.14
    assert val_float("0.0") == 0.0
    assert val_float("-1.5") == -1.5


def test_val_float_single_invalid_type():
    """Test validation with invalid type."""
    with pytest.raises(TypeError):
        val_float(None)
    with pytest.raises(TypeError):
        val_float("invalid_string")


def test_val_float_single_min_value():
    """Test validation with minimum value constraint."""
    assert val_float(5.0, min_value=0.0) == 5.0
    assert val_float(0.0, min_value=0.0) == 0.0

    with pytest.raises(ValueError, match="less than minimum"):
        val_float(-1.0, min_value=0.0)


def test_val_float_single_max_value():
    """Test validation with maximum value constraint."""
    assert val_float(5.0, max_value=10.0) == 5.0
    assert val_float(10.0, max_value=10.0) == 10.0

    with pytest.raises(ValueError, match="greater than maximum"):
        val_float(11.0, max_value=10.0)


def test_val_float_single_min_max_value():
    """Test validation with both min and max value constraints."""
    assert val_float(5.0, min_value=0.0, max_value=10.0) == 5.0
    assert val_float(0.0, min_value=0.0, max_value=10.0) == 0.0
    assert val_float(10.0, min_value=0.0, max_value=10.0) == 10.0

    with pytest.raises(ValueError, match="less than minimum"):
        val_float(-1.0, min_value=0.0, max_value=10.0)

    with pytest.raises(ValueError, match="greater than maximum"):
        val_float(11.0, min_value=0.0, max_value=10.0)


def test_val_float_conflicting_min_max():
    """Test validation with conflicting min and max values."""
    with pytest.raises(ArgumentConflictError, match="min_value must be less than"):
        val_float(5.0, min_value=10.0, max_value=5.0)

    with pytest.raises(ArgumentConflictError):
        val_float(5.0, min_value=5.0, max_value=5.0)


def test_val_float_list_valid():
    """Test validation of list of valid floats."""
    assert val_float([1.0, 2.0, 3.0]) == [1.0, 2.0, 3.0]
    assert val_float([1, 2, 3]) == [1.0, 2.0, 3.0]
    assert val_float(["1.0", "2.0", "3.0"]) == [1.0, 2.0, 3.0]


def test_val_float_list_empty():
    """Test validation of empty list."""
    assert val_float([]) == []


def test_val_float_list_single_element():
    """Test validation of list with single element."""
    assert val_float([3.14]) == [3.14]


def test_val_float_list_n_values():
    """Test validation with n_values constraint."""
    assert val_float([1.0, 2.0, 3.0], n_values=3) == [1.0, 2.0, 3.0]

    with pytest.raises(ValueError, match="is of length"):
        val_float([1.0, 2.0], n_values=3)

    with pytest.raises(ValueError, match="is of length"):
        val_float([1.0, 2.0, 3.0, 4.0], n_values=3)


def test_val_float_list_min_value():
    """Test validation of list with minimum value constraint."""
    assert val_float([1.0, 2.0, 3.0], min_value=0.0) == [1.0, 2.0, 3.0]

    with pytest.raises(ValueError, match="less than minimum"):
        val_float([1.0, -1.0, 3.0], min_value=0.0)


def test_val_float_list_max_value():
    """Test validation of list with maximum value constraint."""
    assert val_float([1.0, 2.0, 3.0], max_value=10.0) == [1.0, 2.0, 3.0]

    with pytest.raises(ValueError, match="greater than maximum"):
        val_float([1.0, 11.0, 3.0], max_value=10.0)


def test_val_float_list_invalid_type():
    """Test validation of list with invalid element type."""
    with pytest.raises(TypeError):
        val_float([1.0, None, 3.0])

    with pytest.raises(TypeError):
        val_float([1.0, "invalid", 3.0])


def test_val_float_tuple():
    """Test validation of tuple of floats."""
    assert val_float((1.0, 2.0, 3.0)) == [1.0, 2.0, 3.0]


def test_val_float_generator():
    """Test validation of generator of floats."""
    result = val_float(x for x in [1.0, 2.0, 3.0])
    assert result == [1.0, 2.0, 3.0]
