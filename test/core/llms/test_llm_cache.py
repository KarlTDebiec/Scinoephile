#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of LLM response caching."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import MonkeyPatch, raises

from scinoephile.core.llms.cache import LlmCache
from test.helpers.files import set_mtime


def test_llm_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = LlmCache(None, "translation")
    cache_path = cache.get_path("provider", "system", "tools", "query")

    cache.save(cache_path, "response")

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache.operation == "translation"
    assert cache_path.parent == runtime_cache_root_path / "llms" / "translation"
    assert cache.load(cache_path) == "response"


def test_llm_cache_path_includes_cache_version(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test LLM cache paths differ between cache versions."""
    cache = LlmCache(tmp_path, "translation")
    first_cache_path = cache.get_path("provider", "system", "tools", "query")

    monkeypatch.setattr("scinoephile.core.llms.cache._CACHE_VERSION", 2)

    assert cache.get_path("provider", "system", "tools", "query") != first_cache_path


def test_llm_cache_uses_operation_subdirectories(tmp_path: Path):
    """Test LLM operations use independent cache subdirectories."""
    translation_cache = LlmCache(tmp_path, "translation")
    review_cache = LlmCache(tmp_path, "review")

    translation_path = translation_cache.get_path(
        "provider", "system", "tools", "query"
    )
    review_path = review_cache.get_path("provider", "system", "tools", "query")

    assert translation_path.parent == tmp_path / "llms" / "translation"
    assert review_path.parent == tmp_path / "llms" / "review"
    assert translation_path.name == review_path.name


def test_llm_cache_rejects_unsafe_operation(tmp_path: Path):
    """Test LLM cache operations may not escape the LLM cache directory."""
    with raises(ValueError, match="single contained filename"):
        LlmCache(tmp_path, "../translation")


def test_llm_cache_overwrites_matching_entry_once(tmp_path: Path):
    """Test overwrite refreshes a matching LLM response once per instance."""
    cache = LlmCache(tmp_path, "translation")
    cache_path = cache.get_path("identity", "system", "tools", "query")
    cache.save(cache_path, "stale")
    overwrite_cache = LlmCache(tmp_path, "translation", True)

    assert overwrite_cache.load(cache_path) is None
    overwrite_cache.save(cache_path, "fresh")

    assert overwrite_cache.load(cache_path) == "fresh"


def test_llm_cache_load_marks_entry_used(tmp_path: Path):
    """Test loading a cached response refreshes its pruning timestamp."""
    cache = LlmCache(tmp_path, "translation")
    cache_path = cache.get_path("identity", "system", "tools", "query")
    cache.save(cache_path, "response")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(cache_path, old_timestamp)

    assert cache.load(cache_path) == "response"
    assert cache_path.stat().st_mtime > old_timestamp


def test_llm_cache_removes_matching_entry(tmp_path: Path):
    """Test removing a cached response returns its path when present."""
    cache = LlmCache(tmp_path, "translation")
    cache_path = cache.get_path("identity", "system", "tools", "query")
    cache.save(cache_path, "response")

    assert cache.remove(cache_path) == cache_path
    assert cache.remove(cache_path) is None
    assert not cache_path.exists()
