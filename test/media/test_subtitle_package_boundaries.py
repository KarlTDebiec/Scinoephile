#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of subtitle media package boundaries."""

from __future__ import annotations

from importlib import import_module
from importlib.util import find_spec


def test_internal_subtitle_helpers_are_not_public():
    """Test internal subtitle helpers are not public module APIs."""
    cache = import_module("scinoephile.media.subtitles.cache")
    details = import_module("scinoephile.media.subtitles.details")

    assert not hasattr(cache, "SUBTITLE_ARTIFACT_CACHE_VERSION")
    assert not hasattr(cache, "IMAGE_SERIES_CACHE_VERSION")
    assert not hasattr(cache, "is_valid_subtitle_artifact_cache")
    assert not hasattr(cache, "get_subtitle_stream_cache_key")
    assert not hasattr(cache, "get_cached_image_subtitle_dir_path")
    assert not hasattr(cache, "_hash_cache_payload")
    assert not hasattr(details, "with_subtitle_details")


def test_subtitle_media_modules_live_under_subtitles_package():
    """Test subtitle media helpers live under the subtitles package."""
    assert find_spec("scinoephile.media.subtitles.extraction") is not None
    assert find_spec("scinoephile.media.subtitles.cache") is not None
    assert find_spec("scinoephile.media.subtitles.details") is not None
    assert find_spec("scinoephile.media.subtitles.stats") is not None


def test_script_specific_helpers_live_outside_media():
    """Test script-specific helpers live outside media."""
    assert find_spec("scinoephile.lang.zho.script_analysis.subtitles") is not None
    assert find_spec("scinoephile.lang.zho.subtitle_streams") is not None
    assert find_spec("scinoephile.media.subtitles.script") is None


def test_image_subtitle_cache_helpers_are_merged_into_media_cache():
    """Test rendered image subtitle cache helpers live in media cache."""
    cache = import_module("scinoephile.media.subtitles.cache")

    assert hasattr(cache, "get_or_create_image_subtitle_dir_path")
    assert hasattr(cache, "is_valid_image_subtitle_cache")
    assert hasattr(cache, "load_cached_image_subtitles")
    assert hasattr(cache, "load_image_subtitle_manifest")
    assert hasattr(cache, "save_image_subtitle_manifest")
    assert find_spec("scinoephile.media.subtitles.image_cache") is None
    assert find_spec("scinoephile.image.subtitles.cache") is None


def test_subtitle_media_package_has_no_function_reexports():
    """Test subtitle media package does not re-export helper functions."""
    subtitles = import_module("scinoephile.media.subtitles")

    assert not hasattr(subtitles, "extract_subtitle_stream")
    assert not hasattr(subtitles, "cache_subtitle_streams")
    assert not hasattr(subtitles, "with_stream_details")


def test_old_subtitle_analysis_package_is_removed():
    """Test old subtitle analysis package path is removed."""
    assert find_spec("scinoephile.media.subtitle_analysis") is None
    assert find_spec("scinoephile.media.subtitles.analysis") is None
