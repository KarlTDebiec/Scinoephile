#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaCli."""

from __future__ import annotations

import pytest

from scinoephile.cli.media.media_cli import MediaCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (MediaCli,),
        (ScinoephileCli, MediaCli),
    ],
)
def test_media_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test media CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (MediaCli,),
        (ScinoephileCli, MediaCli),
    ],
)
def test_media_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test media CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)
