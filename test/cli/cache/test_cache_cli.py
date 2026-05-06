#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache CLI parent command."""

from __future__ import annotations

from scinoephile.cli.cache import CacheCli
from scinoephile.cli.cache.cache_clear_cli import CacheClearCli
from scinoephile.cli.cache.cache_list_cli import CacheListCli
from scinoephile.cli.cache.cache_prune_cli import CachePruneCli
from scinoephile.cli.cache.cache_stats_cli import CacheStatsCli
from test.helpers import assert_cli_help, assert_cli_usage


def test_cache_help():
    """Test cache CLI help output."""
    assert_cli_help((CacheCli,))


def test_cache_usage():
    """Test cache CLI usage output."""
    assert_cli_usage((CacheCli,))


def test_cache_subcommand_help():
    """Test cache subcommand help output."""
    for cli_class in (CacheClearCli, CacheListCli, CachePruneCli, CacheStatsCli):
        assert_cli_help((CacheCli, cli_class))
