#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ScinoephileCli."""

from __future__ import annotations

from scinoephile.cli import ScinoephileCli
from scinoephile.common.testing import assert_cli_help, assert_cli_usage


def test_scinoephile_help():
    """Test root CLI help output."""
    assert_cli_help((ScinoephileCli,))


def test_scinoephile_usage():
    """Test root CLI usage output."""
    assert_cli_usage((ScinoephileCli,))
