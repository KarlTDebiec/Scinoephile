#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of enum argument parsing helpers."""

from __future__ import annotations

from enum import StrEnum

from scinoephile.common.argument_parsing import (
    enum_metavar,
    enum_options,
    enum_options_list_str,
)


class ExampleMode(StrEnum):
    """Example enum for argument parsing tests."""

    AUTO = "auto"
    """Automatic mode."""
    ON = "on"
    """On mode."""
    OFF = "off"
    """Off mode."""


def test_enum_options_returns_values():
    """Test enum_options returns enum values in declaration order."""
    assert enum_options(ExampleMode) == ("auto", "on", "off")


def test_enum_options_list_str_formats_values():
    """Test enum_options_list_str formats enum values for help text."""
    assert enum_options_list_str(ExampleMode) == "auto, on, or off"


def test_enum_metavar_formats_values():
    """Test enum_metavar formats enum values for argparse help."""
    assert enum_metavar(ExampleMode) == "{auto,on,off}"
