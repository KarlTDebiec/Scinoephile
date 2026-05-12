#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Chinese subtitle stream helpers."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from scinoephile.core.media import SubtitleStream
from scinoephile.core.media.language import is_chinese
from scinoephile.media.subtitles.details import get_detailed_subtitle_streams

from .analysis import analyze_zho_subtitle_stream_script

__all__ = ["get_zho_subtitle_streams"]


def get_zho_subtitle_streams(
    infile_path: Path,
    *,
    cache_dir_path: Path | None = None,
) -> list[SubtitleStream]:
    """Get subtitle stream metadata enriched with Chinese script details.

    Arguments:
        infile_path: media input file to inspect
        cache_dir_path: cache directory path
    Returns:
        enriched subtitle stream metadata
    """
    streams = []
    for stream in get_detailed_subtitle_streams(
        infile_path,
        cache_dir_path=cache_dir_path,
    ):
        language = stream.language
        if not is_chinese(language):
            streams.append(stream)
            continue

        analysis = analyze_zho_subtitle_stream_script(
            infile_path,
            stream,
            cache_dir_path=cache_dir_path,
        )
        language = language.split("-", 1)[0]
        if language == "chi":
            language = "zho"
        if analysis.script is not None:
            script = analysis.script.split("-", 1)[1]
            language = f"{language}-{script}"
        else:
            language = f"{language}-Unknown"
        streams.append(replace(stream, language=language))
    return streams
