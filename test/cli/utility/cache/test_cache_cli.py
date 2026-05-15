#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache CLI parent command."""

from __future__ import annotations

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.utility.cache import CacheCli
from scinoephile.cli.utility.cache.cache_clear_cli import CacheClearCli
from scinoephile.cli.utility.cache.cache_list_cli import CacheListCli
from scinoephile.cli.utility.cache.cache_prune_cli import CachePruneCli
from scinoephile.cli.utility.cache.cache_stats_cli import CacheStatsCli
from scinoephile.cli.utility.utility_cli import UtilityCli
from scinoephile.common import CommandLineInterface
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (CacheCli,),
        (UtilityCli, CacheCli),
        (ScinoephileCli, UtilityCli, CacheCli),
    ],
)
def test_cache_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache CLI help output."""
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (CacheCli,),
        (UtilityCli, CacheCli),
        (ScinoephileCli, UtilityCli, CacheCli),
    ],
)
def test_cache_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test cache CLI usage output."""
    assert_cli_usage(cli)


def test_cache_subcommand_help():
    """Test cache subcommand help output."""
    for cli_class in (CacheClearCli, CacheListCli, CachePruneCli, CacheStatsCli):
        assert_cli_help((ScinoephileCli, UtilityCli, CacheCli, cli_class))
