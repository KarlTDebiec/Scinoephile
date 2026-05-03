#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.csv."""

from __future__ import annotations

import pytest

from scinoephile.common.csv import (
    parse_csv_int_list,
    parse_csv_str_list,
)


def test_parse_csv_int_list_empty():
    """Test parsing of empty integer list values."""
    with pytest.raises(ValueError, match="--sizes must include at least one integer"):
        parse_csv_int_list(" , ", name="--sizes")


def test_parse_csv_int_list_invalid_value():
    """Test parsing of invalid integer list values."""
    with pytest.raises(ValueError, match="Invalid integer 'x' in --sizes"):
        parse_csv_int_list("1,x,3", name="--sizes")


def test_parse_csv_int_list_values():
    """Test parsing of comma-separated integer list values."""
    assert parse_csv_int_list("1, 2, , 3", name="--sizes") == [1, 2, 3]


def test_parse_csv_str_list_none():
    """Test parsing of None string list."""
    assert parse_csv_str_list(None) == []


def test_parse_csv_str_list_values():
    """Test parsing of comma-separated string list values."""
    assert parse_csv_str_list("a, b ,, c  ") == ["a", "b", "c"]


def test_parse_csv_str_list_whitespace():
    """Test parsing of whitespace-only string list."""
    assert parse_csv_str_list("   ") == []
