#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.YueCli."""

from __future__ import annotations

import pytest

from scinoephile.cli import ScinoephileCli, YueCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (YueCli,),
        (ScinoephileCli, YueCli),
    ],
)
def test_yue_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueCli,),
        (ScinoephileCli, YueCli),
    ],
)
def test_yue_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)
