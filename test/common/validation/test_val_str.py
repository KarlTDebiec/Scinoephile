#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_str."""

from __future__ import annotations

import pytest
from common.validation import val_str  # ty:ignore[unresolved-import]


def test_val_str_valid():
    """Test validation of valid string."""
    assert val_str("option1", ["option1", "option2", "option3"]) == "option1"
    assert val_str("option2", ["option1", "option2", "option3"]) == "option2"


def test_val_str_case_insensitive():
    """Test case-insensitive validation."""
    assert val_str("OPTION1", ["option1", "option2"]) == "option1"
    assert val_str("Option1", ["option1", "option2"]) == "option1"
    assert val_str("option1", ["OPTION1", "OPTION2"]) == "OPTION1"


def test_val_str_invalid_option():
    """Test validation with invalid option."""
    with pytest.raises(ValueError, match="is not one of options"):
        val_str("invalid", ["option1", "option2"])


def test_val_str_from_int():
    """Test validation of string from int."""
    assert val_str(1, ["1", "2", "3"]) == "1"


def test_val_str_invalid_type():
    """Test validation with None value that gets cast to string.

    Note: None is cast to string "None", which becomes "none" when lowercased.
    This doesn't match any of the provided options, so ValueError is raised.
    """
    with pytest.raises(ValueError, match="is not one of options"):
        val_str(None, ["option1", "option2"])


def test_val_str_empty_options():
    """Test validation with empty options list."""
    with pytest.raises(ValueError, match="is not one of options"):
        val_str("any", [])


def test_val_str_single_option():
    """Test validation with single option."""
    assert val_str("only", ["only"]) == "only"
    assert val_str("ONLY", ["only"]) == "only"


def test_val_str_invalid_option_type():
    """Test validation with None in options list.

    Note: None is cast to string "None", which becomes "none" when lowercased.
    The function performs case-insensitive matching, so "none", "None", and
    "NONE" all match the "None" option.
    """
    assert val_str("none", [None, "option2"]) == "None"
    assert val_str("NONE", [None, "option2"]) == "None"
