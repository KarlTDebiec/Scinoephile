#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.MultiCli."""

from __future__ import annotations

import pytest

from scinoephile.cli.multi.multi_cli import MultiCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (MultiCli,),
        (ScinoephileCli, MultiCli),
    ],
)
def test_multi_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test multi CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (MultiCli,),
        (ScinoephileCli, MultiCli),
    ],
)
def test_multi_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test multi CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)
