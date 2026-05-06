#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ScinoephileCli."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from test.helpers import assert_cli_help, assert_cli_usage


def test_scinoephile_help():
    """Test root CLI help output."""
    assert_cli_help((ScinoephileCli,))


def test_scinoephile_usage():
    """Test root CLI usage output."""
    assert_cli_usage((ScinoephileCli,))


def test_scinoephile_help_does_not_create_default_cache_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """Test root help output does not create default cache directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    cache_dir_path = tmp_path / "cache"
    monkeypatch.setenv("SCINOEPHILE_CACHE_DIR", str(cache_dir_path))

    assert_cli_help((ScinoephileCli,))

    assert not cache_dir_path.exists()
