#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the authoritative Scinoephile cache namespace registry."""

from __future__ import annotations

from pathlib import Path

from pytest import raises

from scinoephile.core.cache.cache_namespace import CacheNamespace


class _CacheNamespace(CacheNamespace):
    """Cache namespace declarations for generic behavior tests."""

    OPERATION = "test/<operation>"
    """Parameterized test namespace."""
    STATIC = "test/static"
    """Static test namespace."""


def test_cache_namespace_base_has_no_concrete_members():
    """Test core's generic namespace base has no owner-specific members."""
    assert list(CacheNamespace) == []


def test_parameterized_cache_namespace_validates_operation(tmp_path: Path):
    """Test operation families accept only a contained directory name.

    Arguments:
        tmp_path: temporary cache root path
    """
    namespace = _CacheNamespace.OPERATION

    assert namespace.get_name(operation="translation") == "test/translation"
    assert namespace.get_dir_path(tmp_path, operation="translation") == (
        tmp_path / "test/translation"
    )
    with raises(ValueError, match="requires an operation"):
        namespace.get_name()
    with raises(ValueError, match="single contained filename"):
        namespace.get_name(operation="../translation")


def test_static_cache_namespace_rejects_operation():
    """Test static registry entries reject an extraneous operation name."""
    with raises(ValueError, match="does not accept an operation"):
        _CacheNamespace.STATIC.get_name(operation="unexpected")
