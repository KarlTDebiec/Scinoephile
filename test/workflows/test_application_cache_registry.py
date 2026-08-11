#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the application-wide cache namespace registry."""

from __future__ import annotations

from scinoephile.workflows.cache_registry import CACHE_REGISTRY


def test_cache_registry_matches_owned_layout():
    """Test the registry contains the complete Scinoephile-owned cache layout."""
    assert {namespace.value for namespace in CACHE_REGISTRY} == {
        "cuhk-discovery",
        "cuhk-pages",
        "demucs",
        "google-lens",
        "llm/<operation>",
        "media/subtitles",
        "media/subtitles/analysis",
        "mlx-audio",
        "paddleocr",
        "tesseract",
        "tesseract-legacy-data",
        "whisper",
    }
