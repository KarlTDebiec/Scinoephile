#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle extraction from media files."""

from __future__ import annotations

from pathlib import Path
from shutil import copy2

from scinoephile.core.media import SubtitleStream

from .cache import (
    cache_subtitle_stream_artifacts,
    get_cached_subtitle_artifact_path,
    is_valid_subtitle_artifact_cache,
)

__all__ = ["extract_subtitle_stream"]


def extract_subtitle_stream(
    infile_path: Path,
    stream: SubtitleStream,
    outfile_path: Path,
    *,
    cache_dir_path: Path | None = None,
) -> Path:
    """Extract a subtitle stream using a runtime artifact cache.

    Arguments:
        infile_path: media input file
        stream: subtitle stream to extract
        outfile_path: requested output path
        cache_dir_path: cache directory path
    Returns:
        output path
    """
    artifact_path = get_cached_subtitle_artifact_path(
        infile_path,
        stream,
        cache_dir_path=cache_dir_path,
    )
    if not is_valid_subtitle_artifact_cache(artifact_path):
        cache_subtitle_stream_artifacts(
            infile_path,
            [stream],
            cache_dir_path=cache_dir_path,
        )
    if artifact_path.resolve() != outfile_path.resolve():
        outfile_path.parent.mkdir(parents=True, exist_ok=True)
        copy2(artifact_path, outfile_path)
    return outfile_path
