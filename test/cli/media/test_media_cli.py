#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaCli."""

from __future__ import annotations

from scinoephile.cli.media.media_cli import MediaCli


def test_media_cli_includes_search_subs_subcommand():
    """Test media CLI registers the search-subs subcommand."""
    assert "search-subs" in MediaCli.subcommands()
