#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache CLI argument type helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scinoephile.cli.helpers.cache import cache_dir_path_arg


def test_cache_dir_path_arg_resolves_runtime_cache_subpath():
    """Test cache directory defaults may include runtime cache subpath parts."""
    with patch(
        "scinoephile.cli.helpers.cache.get_runtime_cache_dir_path",
        return_value=Path("/cache/media/subtitles"),
    ) as get_runtime_cache_dir_path:
        cache_dir_path = cache_dir_path_arg("media", "subtitles")

    assert cache_dir_path == Path("/cache/media/subtitles")
    get_runtime_cache_dir_path.assert_called_once_with(
        "media",
        "subtitles",
        create=False,
    )


def test_cache_dir_path_arg_resolves_user_path_without_creating(tmp_path: Path):
    """Test cache directory CLI paths are resolved without parser-time creation.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    cache_dir_path = tmp_path / "cache"

    resolved_cache_dir_path = cache_dir_path_arg(str(cache_dir_path))

    assert resolved_cache_dir_path == cache_dir_path.resolve()
    assert not cache_dir_path.exists()
