#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle media package boundaries."""

from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec


def test_internal_subtitle_helpers_are_not_public():
    """Test internal subtitle helpers are not public module APIs."""
    cache = import_module("scinoephile.media.subtitles.cache")
    cache_keys = import_module("scinoephile.media.subtitles.analysis.cache_keys")
    details = import_module("scinoephile.media.subtitles.analysis.details")
    image_cache = import_module("scinoephile.media.subtitles.analysis.image_cache")

    assert not hasattr(cache, "get_subtitle_stream_cache_key")
    assert not hasattr(cache_keys, "get_subtitle_analysis_cache_key")
    assert not hasattr(details, "with_subtitle_details")
    assert not hasattr(image_cache, "get_cached_image_subtitle_dir_path")
    assert not hasattr(image_cache, "is_valid_image_subtitle_cache")


def test_subtitle_media_modules_live_under_subtitles_package():
    """Test subtitle media helpers live under the subtitles package."""
    assert find_spec("scinoephile.media.subtitles.extraction") is not None
    assert find_spec("scinoephile.media.subtitles.cache") is not None
    assert find_spec("scinoephile.media.subtitles.analysis") is not None


def test_subtitle_media_package_has_no_function_reexports():
    """Test subtitle media package does not re-export helper functions."""
    subtitles = import_module("scinoephile.media.subtitles")

    assert not hasattr(subtitles, "extract_subtitle_stream")
    assert not hasattr(subtitles, "cache_subtitle_stream_artifacts")
    assert not hasattr(subtitles, "with_stream_details")


def test_old_subtitle_analysis_package_is_removed():
    """Test old subtitle analysis package path is removed."""
    assert find_spec("scinoephile.media.subtitle_analysis") is None
