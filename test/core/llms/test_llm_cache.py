#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of LLM response caching."""

from __future__ import annotations

from pathlib import Path
from time import time

from pytest import MonkeyPatch, raises

from scinoephile.core.llms.cache import LlmCache
from test.helpers import parametrize
from test.helpers.files import set_mtime

_CACHE_INPUTS = ("provider", "system", "[]", '{"query":"value"}')
"""Valid serialized inputs shared by LLM cache tests."""


def test_llm_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = LlmCache(None, "translation")
    cache_path = cache.get_path(*_CACHE_INPUTS)

    cache.save(*_CACHE_INPUTS, "response")

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache.operation == "translation"
    assert cache_path.parent == runtime_cache_root_path / "llms" / "translation"
    assert cache.load(*_CACHE_INPUTS) == "response"


def test_llm_cache_path_includes_cache_version(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Test LLM cache paths differ between cache versions."""
    cache = LlmCache(tmp_path, "translation")
    first_cache_path = cache.get_path(*_CACHE_INPUTS)

    monkeypatch.setattr("scinoephile.core.llms.cache._CACHE_VERSION", 3)

    assert cache.get_path(*_CACHE_INPUTS) != first_cache_path


def test_llm_cache_uses_operation_subdirectories(tmp_path: Path):
    """Test LLM operations use independent cache subdirectories."""
    translation_cache = LlmCache(tmp_path, "translation")
    review_cache = LlmCache(tmp_path, "review")

    translation_path = translation_cache.get_path(*_CACHE_INPUTS)
    review_path = review_cache.get_path(*_CACHE_INPUTS)

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
    cache.save(*_CACHE_INPUTS, "stale")
    overwrite_cache = LlmCache(tmp_path, "translation", True)

    assert overwrite_cache.load(*_CACHE_INPUTS) is None
    overwrite_cache.save(*_CACHE_INPUTS, "fresh")

    assert overwrite_cache.load(*_CACHE_INPUTS) == "fresh"


def test_llm_cache_load_marks_entry_used(tmp_path: Path):
    """Test loading a cached response refreshes its pruning timestamp."""
    cache = LlmCache(tmp_path, "translation")
    cache_path = cache.get_path(*_CACHE_INPUTS)
    cache.save(*_CACHE_INPUTS, "response")
    old_timestamp = time() - 60 * 60 * 24 * 40
    set_mtime(cache_path, old_timestamp)

    assert cache.load(*_CACHE_INPUTS) == "response"
    assert cache_path.stat().st_mtime > old_timestamp


def test_llm_cache_removes_matching_entry(tmp_path: Path):
    """Test removing a cached response returns its path when present."""
    cache = LlmCache(tmp_path, "translation")
    cache_path = cache.get_path(*_CACHE_INPUTS)
    cache.save(*_CACHE_INPUTS, "response")

    assert cache.remove(*_CACHE_INPUTS) == cache_path
    assert cache.remove(*_CACHE_INPUTS) is None
    assert not cache_path.exists()


def test_llm_cache_path_encodes_component_boundaries(tmp_path: Path):
    """Test text moved across identity fields cannot produce the same key."""
    cache = LlmCache(tmp_path, "translation")

    first_path = cache.get_path("provider", "system[]", "", '{"query":"value"}')
    second_path = cache.get_path("provider", "system", "[]", '{"query":"value"}')

    assert first_path != second_path


@parametrize("artifact_type", ["directory", "symlink", "broken_symlink"])
def test_llm_cache_discards_wrong_filesystem_type(tmp_path: Path, artifact_type: str):
    """Test an expected response file with the wrong type becomes a miss.

    Arguments:
        tmp_path: temporary directory provided by pytest
        artifact_type: malformed artifact type to create
    """
    cache = LlmCache(tmp_path, "translation")
    cache_path = cache.get_path(*_CACHE_INPUTS)
    target_path = tmp_path / "target.json"
    if artifact_type == "directory":
        cache_path.mkdir()
    elif artifact_type == "symlink":
        target_path.write_text("target", encoding="utf-8")
        cache_path.symlink_to(target_path)
    else:
        cache_path.symlink_to(target_path)

    assert cache.load(*_CACHE_INPUTS) is None
    assert not cache_path.exists()
    assert not cache_path.is_symlink()
    if artifact_type == "symlink":
        assert target_path.read_text(encoding="utf-8") == "target"
