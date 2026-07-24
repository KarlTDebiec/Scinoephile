#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle stream helpers."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from scinoephile.core.language import is_chinese_language_tag
from scinoephile.core.media import Stream, SubtitleStream
from scinoephile.media.subtitles.details import get_detailed_subtitle_streams

from .analysis import analyze_zho_subtitle_stream_script

__all__ = ["get_zho_subtitle_streams"]


def get_zho_subtitle_streams(
    infile_path: Path,
    *,
    cache_dir_path: Path | None = None,
    overwrite_cache: bool = False,
    streams: Sequence[Stream] | None = None,
) -> list[SubtitleStream]:
    """Get subtitle stream metadata enriched with Chinese script details.

    Arguments:
        infile_path: media input file to inspect
        cache_dir_path: cache root directory path
        overwrite_cache: whether to replace matching cached subtitle artifacts
        streams: optional pre-probed media streams
    Returns:
        enriched subtitle stream metadata
    """
    subtitle_cache_dir_path = None
    if cache_dir_path is not None:
        subtitle_cache_dir_path = cache_dir_path / "media" / "subtitles"
    zho_streams = []
    for stream in get_detailed_subtitle_streams(
        infile_path,
        cache_dir_path=subtitle_cache_dir_path,
        overwrite_cache=overwrite_cache,
        streams=streams,
    ):
        language = stream.language
        if language is None or not is_chinese_language_tag(language):
            zho_streams.append(stream)
            continue

        analysis = analyze_zho_subtitle_stream_script(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
            overwrite_cache=overwrite_cache,
            subtitle_cache_is_fresh=overwrite_cache,
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
