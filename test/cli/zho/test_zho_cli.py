#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoCli."""

from __future__ import annotations

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.zho.zho_cli import ZhoCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoCli,),
        (ScinoephileCli, ZhoCli),
    ],
)
def test_zho_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (ZhoCli,),
        (ScinoephileCli, ZhoCli),
    ],
)
def test_zho_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test standard Chinese CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)
