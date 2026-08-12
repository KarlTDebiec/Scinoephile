#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the generic cache namespace registry."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.core.cache.cache_namespace import CacheNamespace
from scinoephile.core.cache.cache_registry import CacheRegistry


class _CacheNamespace(CacheNamespace):
    """Cache namespace declarations for registry tests."""

    FAMILY = "family/<operation>"
    """Parameterized test namespace."""
    STATIC = "static"
    """Static test namespace."""


class _DuplicateCacheNamespace(CacheNamespace):
    """Duplicate cache namespace declaration for registry tests."""

    STATIC = "static"
    """Static test namespace duplicating another declaration."""


def test_cache_registry_discovers_registered_namespaces(tmp_path: Path):
    """Test a registry discovers only its declared namespace layouts.

    Arguments:
        tmp_path: temporary cache root path
    """
    (tmp_path / "family/translation").mkdir(parents=True)
    (tmp_path / "static").mkdir()
    (tmp_path / "unregistered").mkdir()

    registry = CacheRegistry(_CacheNamespace)

    assert registry.discover_names(tmp_path) == ["family/translation", "static"]


def test_cache_registry_rejects_duplicate_templates():
    """Test a registry rejects duplicate namespace templates."""
    with raises(ValueError, match="Duplicate cache namespace templates: static"):
        CacheRegistry((*_CacheNamespace, *_DuplicateCacheNamespace))
