#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle stream script analysis."""

from __future__ import annotations

from .artifacts import (
    cache_subtitle_stream_artifacts,
    extract_subtitle_stream_from_cache,
    get_cached_subtitle_artifact_path,
)
from .details import with_stream_details, with_subtitle_details
from .image_cache import get_cached_image_subtitle_dir_path
from .script import analyze_subtitle_stream_script
from .stats import (
    count_subtitle_stream_events,
    format_stream_span_time,
    get_subtitle_stream_stats,
)
from .types import SubtitleScriptAnalysis, SubtitleStreamStats

__all__ = [
    "SubtitleScriptAnalysis",
    "SubtitleStreamStats",
    "analyze_subtitle_stream_script",
    "cache_subtitle_stream_artifacts",
    "count_subtitle_stream_events",
    "extract_subtitle_stream_from_cache",
    "format_stream_span_time",
    "get_cached_image_subtitle_dir_path",
    "get_cached_subtitle_artifact_path",
    "get_subtitle_stream_stats",
    "with_stream_details",
    "with_subtitle_details",
]
