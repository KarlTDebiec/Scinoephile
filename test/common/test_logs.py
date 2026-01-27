#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.logs."""

from __future__ import annotations

from logging import DEBUG, ERROR, INFO, WARNING, getLogger

from common.logs import set_logging_verbosity  # ty:ignore[unresolved-import]


def test_set_logging_verbosity_error():
    """Test setting logging verbosity to ERROR level."""
    set_logging_verbosity(0)
    assert getLogger().level == ERROR


def test_set_logging_verbosity_warning():
    """Test setting logging verbosity to WARNING level."""
    set_logging_verbosity(1)
    assert getLogger().level == WARNING


def test_set_logging_verbosity_info():
    """Test setting logging verbosity to INFO level."""
    set_logging_verbosity(2)
    assert getLogger().level == INFO


def test_set_logging_verbosity_debug():
    """Test setting logging verbosity to DEBUG level."""
    set_logging_verbosity(3)
    assert getLogger().level == DEBUG


def test_set_logging_verbosity_debug_high():
    """Test setting logging verbosity to DEBUG level with high value."""
    set_logging_verbosity(10)
    assert getLogger().level == DEBUG
