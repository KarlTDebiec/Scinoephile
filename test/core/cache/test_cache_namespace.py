#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the authoritative Scinoephile cache namespace registry."""

from __future__ import annotations

from pathlib import Path

from pytest import MonkeyPatch, raises

from scinoephile.core.cache.cache_namespace import CacheNamespace
from test.helpers import create_symlink_or_skip


class _CacheNamespace(CacheNamespace):
    """Cache namespace declarations for generic behavior tests."""

    OPERATION = "test/<operation>"
    """Parameterized test namespace."""
    STATIC = "test/static"
    """Static test namespace."""


class _InvalidCacheNamespace(CacheNamespace):
    """Invalid cache namespace declarations for validation tests."""

    ABSOLUTE = "/test/static"
    """Absolute namespace path."""
    COLON = "test/model:version"
    """Namespace path containing an invalid Windows character."""
    MISPLACED_OPERATION = "test/<operation>/static"
    """Namespace with a nonterminal operation placeholder."""
    RESERVED = "test/aux.txt"
    """Namespace path containing a Windows-reserved device name."""
    TRAILING_DOT = "test/operation."
    """Namespace path containing a Windows-incompatible trailing dot."""
    TRAVERSAL = "test/../static"
    """Namespace path that traverses its parent."""
    WILDCARD = "test/*"
    """Namespace path containing an invalid Windows wildcard."""


def test_cache_namespace_base_has_no_concrete_members():
    """Test core's generic namespace base has no owner-specific members."""
    assert list(CacheNamespace) == []


def test_parameterized_cache_namespace_validates_operation_and_creates_directory(
    tmp_path: Path,
):
    """Test operation families create a directory for a valid contained name.

    Arguments:
        tmp_path: temporary cache root path
    """
    namespace = _CacheNamespace.OPERATION

    namespace_dir_path = namespace.get_dir_path(tmp_path, operation="translation")

    assert namespace.get_name(operation="translation") == "test/translation"
    assert namespace_dir_path == tmp_path / "test/translation"
    assert namespace_dir_path.is_dir()
    with raises(ValueError, match="requires an operation"):
        namespace.get_name()
    for operation in ("../translation", "CON", "aux.txt", "foo.", "foo ", "*", "a:b"):
        with raises(ValueError, match="single contained filename"):
            namespace.get_name(operation=operation)


def test_parameterized_cache_namespace_validation_is_cwd_independent(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test operation validation does not resolve names against the working directory.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    target_dir_path = tmp_path / "target"
    target_dir_path.mkdir()
    create_symlink_or_skip(
        tmp_path / "translation", target_dir_path, target_is_directory=True
    )
    monkeypatch.chdir(tmp_path)

    assert _CacheNamespace.OPERATION.get_name(operation="translation") == (
        "test/translation"
    )


def test_cache_namespace_rejects_invalid_templates():
    """Test namespace templates must be portable relative paths."""
    for namespace in _InvalidCacheNamespace:
        with raises(ValueError, match="portable relative path"):
            namespace.get_name()


def test_cache_namespace_rejects_symlinked_ancestor(tmp_path: Path):
    """Test namespace paths do not traverse symlinked directories.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    cache_root_path = tmp_path / "cache"
    cache_root_path.mkdir()
    outside_dir_path = tmp_path / "outside"
    (outside_dir_path / "static").mkdir(parents=True)
    create_symlink_or_skip(
        cache_root_path / "test", outside_dir_path, target_is_directory=True
    )

    assert _CacheNamespace.STATIC.discover_names(cache_root_path) == []
    with raises(ValueError, match="traverses symbolic link"):
        _CacheNamespace.STATIC.get_dir_path(cache_root_path)


def test_static_cache_namespace_rejects_operation():
    """Test static registry entries reject an extraneous operation name."""
    with raises(ValueError, match="does not accept an operation"):
        _CacheNamespace.STATIC.get_name(operation="unexpected")
