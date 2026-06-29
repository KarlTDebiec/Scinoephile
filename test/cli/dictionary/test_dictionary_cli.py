#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.DictionaryCli."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch

from scinoephile.cli.dictionary.dictionary_cli import DictionaryCli
from test.helpers import assert_cli_usage


def test_dictionary_usage_does_not_create_default_cache_dir(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test dictionary usage output does not create default cache directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    cache_dir_path = tmp_path / "cache"
    monkeypatch.setenv("SCINOEPHILE_CACHE_DIR", str(cache_dir_path))

    assert_cli_usage((DictionaryCli,))

    assert not cache_dir_path.exists()
