#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of cache CLI argument type helpers."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import patch

from pytest import raises

from scinoephile.cli.helpers.cache import (
    CacheArguments,
    add_cache_args,
    add_cache_dir_arg,
)


def test_add_cache_args_bundles_root_and_overwrite(tmp_path: Path):
    """Test shared cache arguments parse into one bundle.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    parser = ArgumentParser()
    cache_arg_group = parser.add_argument_group("cache arguments")
    cache_dir_path = tmp_path / "cache"

    add_cache_args(cache_arg_group)
    namespace = parser.parse_args(
        ["--cache-dir", str(cache_dir_path), "--cache-overwrite"]
    )

    assert namespace.cache_args == CacheArguments(
        dir_path=cache_dir_path.resolve(),
        overwrite=True,
    )
    assert not cache_dir_path.exists()


def test_add_cache_dir_arg_resolves_runtime_cache_subpath():
    """Test cache directory defaults may include runtime cache subpath parts."""
    parser = ArgumentParser()
    cache_arg_group = parser.add_argument_group("operation arguments")
    runtime_cache_parts: list[tuple[str, ...]] = []
    create_values: list[bool] = []

    def get_runtime_cache_dir_path(*parts: str, create: bool) -> Path:
        """Record runtime cache default arguments."""
        runtime_cache_parts.append(parts)
        create_values.append(create)
        return Path("/cache/media/subtitles")

    with patch(
        "scinoephile.cli.helpers.cache.get_runtime_cache_dir_path",
        side_effect=get_runtime_cache_dir_path,
    ):
        add_cache_dir_arg(cache_arg_group, "media", "subtitles")

    namespace = parser.parse_args([])

    assert namespace.cache_dir_path == Path("/cache/media/subtitles")
    assert runtime_cache_parts == [("media", "subtitles")]
    assert create_values == [False]


def test_add_cache_dir_arg_resolves_user_path_without_creating(tmp_path: Path):
    """Test cache directory CLI paths are resolved without parser-time creation.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    parser = ArgumentParser()
    cache_arg_group = parser.add_argument_group("operation arguments")
    cache_dir_path = tmp_path / "cache"

    add_cache_dir_arg(cache_arg_group)
    namespace = parser.parse_args(["--cache-dir", str(cache_dir_path)])

    assert namespace.cache_dir_path == cache_dir_path.resolve()
    assert not cache_dir_path.exists()


def test_add_cache_dir_arg_rejects_existing_file(tmp_path: Path):
    """Test cache directory CLI paths reject existing files.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    parser = ArgumentParser()
    cache_arg_group = parser.add_argument_group("operation arguments")
    cache_file_path = tmp_path / "cache"
    cache_file_path.write_text("cache", encoding="utf-8")

    add_cache_dir_arg(cache_arg_group)
    with raises(SystemExit) as excinfo:
        parser.parse_args(["--cache-dir", str(cache_file_path)])

    assert excinfo.value.code == 2
