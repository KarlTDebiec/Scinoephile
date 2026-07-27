#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of LLM response caching."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core.llms.cache import LlmCache


def test_llm_cache_uses_runtime_default(runtime_cache_root_path: Path):
    """Test a missing configured root selects the runtime cache root.

    Arguments:
        runtime_cache_root_path: isolated default runtime cache root
    """
    cache = LlmCache(None)
    cache_path = cache.get_path("provider", "system", "tools", "query")

    cache.save(cache_path, "response")

    assert cache.cache_root_path == runtime_cache_root_path
    assert cache_path.parent == runtime_cache_root_path / "llm"
    assert cache.load(cache_path) == "response"
