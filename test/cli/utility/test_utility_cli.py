#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the utility CLI."""

from __future__ import annotations

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.utility.utility_cli import UtilityCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (UtilityCli,),
        (ScinoephileCli, UtilityCli),
    ],
)
def test_utility_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test utility CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (UtilityCli,),
        (ScinoephileCli, UtilityCli),
    ],
)
def test_utility_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test utility CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)
