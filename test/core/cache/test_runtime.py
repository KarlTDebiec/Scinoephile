#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of persistent-cache runtime identities."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from unittest.mock import Mock

from pytest import MonkeyPatch

from scinoephile.core.cache.runtime import get_distribution_identity


def test_get_distribution_identity(monkeypatch: MonkeyPatch):
    """Test distribution identities include the installed version."""
    installed_distribution = Mock(version="1.2.3")
    installed_distribution.read_text.return_value = None
    monkeypatch.setattr(
        "scinoephile.core.cache.runtime.distribution",
        Mock(return_value=installed_distribution),
    )

    assert get_distribution_identity("test-runtime") == {
        "distribution": "test-runtime",
        "version": "1.2.3",
    }


def test_get_distribution_identity_includes_vcs_revision(monkeypatch: MonkeyPatch):
    """Test VCS distributions include their installed commit revision."""
    installed_distribution = Mock(version="1.2.3")
    installed_distribution.read_text.return_value = """{
        "url": "https://example.com/runtime.git",
        "vcs_info": {
            "commit_id": "immutable-commit",
            "requested_revision": "main",
            "vcs": "git"
        }
    }"""
    monkeypatch.setattr(
        "scinoephile.core.cache.runtime.distribution",
        Mock(return_value=installed_distribution),
    )

    assert get_distribution_identity("test-runtime") == {
        "distribution": "test-runtime",
        "version": "1.2.3",
        "source_revision": "immutable-commit",
    }


def test_get_distribution_identity_handles_missing_distribution(
    monkeypatch: MonkeyPatch,
):
    """Test missing distributions produce a stable unavailable identity."""
    monkeypatch.setattr(
        "scinoephile.core.cache.runtime.distribution",
        Mock(side_effect=PackageNotFoundError),
    )

    assert get_distribution_identity("test-runtime") == {
        "distribution": "test-runtime",
        "version": "unavailable",
    }
