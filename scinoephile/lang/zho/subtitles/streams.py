#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle stream helpers."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from scinoephile.core.language import is_chinese_language_tag
from scinoephile.core.media import Stream, SubtitleStream
from scinoephile.core.paths import get_runtime_cache_root_path
from scinoephile.media.subtitles.cache import SubtitleCache
from scinoephile.media.subtitles.details import get_detailed_subtitle_streams

from .analysis.script import analyze_zho_subtitle_stream_script

__all__ = ["get_zho_subtitle_streams"]


def get_zho_subtitle_streams(
    infile_path: Path,
    *,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    streams: Sequence[Stream] | None = None,
    subtitle_cache: SubtitleCache | None = None,
) -> list[SubtitleStream]:
    """Get subtitle stream metadata enriched with Chinese script details.

    Arguments:
        infile_path: media input file to inspect
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching cached subtitle artifacts
        streams: optional pre-probed media streams
        subtitle_cache: subtitle stream cache shared with upstream operations
    Returns:
        enriched subtitle stream metadata
    """
    if subtitle_cache is None:
        if cache_root_path is None:
            cache_root_path = get_runtime_cache_root_path()
        subtitle_cache = SubtitleCache(cache_root_path, overwrite_cache)
    else:
        cache_root_path = subtitle_cache.cache_root_path
        overwrite_cache = subtitle_cache.overwrite

    zho_streams = []
    for stream in get_detailed_subtitle_streams(
        infile_path,
        streams=streams,
        subtitle_cache=subtitle_cache,
    ):
        language = stream.language
        if language is None or not is_chinese_language_tag(language):
            zho_streams.append(stream)
            continue

        analysis = analyze_zho_subtitle_stream_script(
            infile_path,
            stream,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            subtitle_cache=subtitle_cache,
        )
        language = language.split("-", 1)[0]
        if language == "chi":
            language = "zho"
        if analysis.script is not None:
            script = analysis.script.split("-", 1)[1]
            language = f"{language}-{script}"
        else:
            language = f"{language}-Unknown"
        stream.language = language
        zho_streams.append(stream)
    return zho_streams
